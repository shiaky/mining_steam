import urllib3
import json
import numpy as np
from random import randint
from threading import Thread, Lock

import time


class Player(object):
    def __init__(self):
        self.Id = None
        self.SteamName = None
        self.LastLogOff = None
        self.RealName = None
        self.PrimaryClanId = None
        self.TimeCreated = None
        self.Country = None
        self.State = None
        self.City = None
        self.PrivacyState = None
        self.Banned = False
        self.DaysSinceLastBan = 0
        self.Friends = []
        self.OwnedGames = []
        self.crawlFriends = []
        self.crawledFriends = []
        self.crawled = False


class OwnedGame(object):
    def __init__(self):
        self.Id = None
        self.PlaytimeForever = 0
        self.Playtime2Weeks = 0
        self.Achievements = {}


class Game(object):
    def __init__(self):
        self.Id = None
        self.Name = None
        self.HasAchievements = False
        self.Achievements = {}
        self.IsFree = None
        self.Genres = None


class SteamCrawler(object):
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.numberOfPlayers = 0
        self.http = urllib3.PoolManager()
        self.newestAvailableSteamAccount = 76561198439825722
        self.oldestAvailableSteamAccount = 76561197962316888
        self.playerIds = []
        self.Games = {}
        self.Players = {}
        self.CrawledPlayers = set()
        self.CrawledGames = set()
        self.gamesToCrawl = []
        self.apiCalls = 0
        self.specialApiCalls = 0
        self.specialApiTime = int(time.time())
        self.firstSpecialApi = True
        self.apiRateLimit = 100000 - 5
        self.specialApiRateLimit = 200 - 5
        self.GamesToSkip = {}
        self.finishedGames = {}
        self.crawlPlayerAchievements = None
        self.apiCallLock = Lock()
        self.gameListLock = Lock()
        self.continueToCrawlGamesLock = Lock()
        self.stopGameThread = False
        self.gameThreadStopped = False
        self.gameThread = None
        self.creationTime = int(time.time())

    def __executeApiCall(self, call, specialApi=False):
        self.apiCallLock.acquire()
        self.apiCalls += 1
        if self.apiCalls == self.apiRateLimit:
            now = int(time.time())
            timeDelta = now - self.creationTime
            sleepTime = (60 * 60 * 24) - timeDelta
            if sleepTime > 0:
                print("Maximum calls per day reached, sleeping for " +
                      str(sleepTime) + " seconds.")
                time.sleep(sleepTime)
                self.apiCalls = 0
                self.creationTime = int(time.time())
        if self.apiCalls >= self.apiRateLimit:
            return None, 666
        if specialApi:
            if self.firstSpecialApi:
                self.firstSpecialApi = False
                self.specialApiTime = int(time.time())
            self.specialApiCalls += 1
            if self.specialApiCalls >= self.specialApiRateLimit:
                timeDelta = int(time.time()) - self.specialApiTime
                if timeDelta <= (60 * 5):
                    sleepTime = (60 * 5) - timeDelta
                    self.apiCallLock.release()
                    print("Special Api Rate Limit exceeded, second thread sleeping for " +
                          str(sleepTime) + " seconds (first thread continues crawling)")
                    time.sleep(sleepTime)
                    self.apiCallLock.acquire()
                    self.specialApiTime = int(time.time())
                    self.specialApiCalls = 0

        r = self.http.request('GET', call)
        resultString = None
        status = 666
        if not r == None:
            resultString = r.data.decode("utf-8")
            if not r.status == None:
                status = r.status
        result = None
        if not resultString == None:
            try:
                result = json.loads(resultString)
            except:
                print("Some error occurred parsing the game data JSON: %s\ncontinue with the next stuff in the queue...." %
                      resultString)
        self.apiCallLock.release()
        return result, status

    def __getPlayerSummaries(self, *playerIds):
        getPlayerSummariesCall = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + \
            self.apiKey + "&steamids="
        playersParam = ""
        for playerId in playerIds:
            playersParam += str(playerId) + ","
        playersParam = playersParam[:-1]
        apiCall = getPlayerSummariesCall + playersParam
        result, status = self.__executeApiCall(apiCall)
        if status == 200:
            return result
        else:
            return None

    def __getPlayerBans(self, *playerIds):
        getPlayerBansCall = "http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key=" + \
            self.apiKey + "&steamids="
        playersParam = ""
        for playerId in playerIds:
            playersParam += str(playerId) + ","
        playersParam = playersParam[:-1]
        getPlayerBansCall += playersParam
        result, status = self.__executeApiCall(getPlayerBansCall)
        if status == 200:
            return result
        else:
            return None

    def __getFriendList(self, playerId):
        getFriendListCall = "http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=" + self.apiKey + "&steamid=" + str(
            playerId) + "&relationship=friend"
        result, status = self.__executeApiCall(getFriendListCall)
        if status == 200:
            return result
        else:
            return None

    def __getPlayerAchievementsForGame(self, playerId, gameId):
        if gameId in self.GamesToSkip:
            return None
        getPlayerAchievementsForGameCall = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid=" + str(
            gameId) + "&key=" + self.apiKey + "&steamid=" + str(playerId)
        result, status = self.__executeApiCall(
            getPlayerAchievementsForGameCall)
        if status == 200:
            return result
        else:
            if "playerstats" in result and "error" in result["playerstats"] and result["playerstats"][
                    "error"] == "Requested app has no stats":
                self.GamesToSkip.update({gameId: True})
            return None

    def __getOwnedGames(self, playerId):
        getOwnedGamesCall = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=" + \
            self.apiKey + "&steamid=" + str(playerId) + "&format=json"
        result, status = self.__executeApiCall(getOwnedGamesCall)
        if status == 200:
            return result
        else:
            return None

    def __getGameDetails(self, appId):
        getGameDetailsCall = "http://store.steampowered.com/api/appdetails?appids=" + \
            str(appId)
        result, status = self.__executeApiCall(getGameDetailsCall, True)
        if status == 200:
            return result
        else:
            return None

    def __getGameAchievements(self, gamedId):
        getGameAchievementsCall = "http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid=" + \
            str(gamedId) + "&format=json"
        result, status = self.__executeApiCall(getGameAchievementsCall)
        if status == 200:
            return result
        else:
            return None

    def __produceGame(self, gameId):
        self.gameListLock.acquire()
        self.CrawledGames.add(gameId)
        self.gamesToCrawl.append(gameId)
        self.__createGame(gameId)
        self.gameListLock.release()

    def __createGame(self, gameId):
        game = Game()
        game.Id = gameId
        gameAchievements = self.__getGameAchievements(gameId)
        if (gameAchievements is not None and "achievementpercentages" in gameAchievements and "achievements" in gameAchievements["achievementpercentages"]):
            gameAchievements = gameAchievements["achievementpercentages"]["achievements"]
            for gameAchievement in gameAchievements:
                game.Achievements.update(
                    {gameAchievement["name"]: float(gameAchievement["percent"])})
            if len(game.Achievements) > 0:
                game.HasAchievements = True
        self.Games.update({game.Id: game})

    def GetRandomPlayerId(self):
        return np.random.randint(self.oldestAvailableSteamAccount, self.newestAvailableSteamAccount + 1)

    def CrawlSteam(self, numberOfPlayers, crawlPlayerAchievements, startPlayer):
        self.Players = {}
        self.crawlPlayerAchievements = crawlPlayerAchievements
        self.numberOfPlayers = numberOfPlayers
        playersToCrawl = self.__getPlayersToCrawl(
            str(startPlayer), numberOfPlayers)
        if self.gameThread is None or not self.gameThread.isAlive():
            if self.gameThread is None:
                self.gameThread = Thread(target=self.__getGameInfos)
            self.gameThread.start()
        for i in range(0, len(playersToCrawl), 100):
            endIndex = (i + 100, len(playersToCrawl)
                        )[i + 100 > len(playersToCrawl)]
            playerSubList = playersToCrawl[i:endIndex]
            self.__assemblePlayers(*playerSubList)
        returnGames = None
        self.gameListLock.acquire()
        returnGames = dict(self.finishedGames)
        self.finishedGames = {}
        self.gameListLock.release()
        return self.Players, returnGames

    def SetCrawledGames(self, gamesList):
        self.CrawledGames.update(gamesList)

    def SetCrawledPlayers(self, playersList):
        self.CrawledPlayers.update(playersList)

    def stopCrawling(self):
        self.continueToCrawlGamesLock.acquire()
        self.stopGameThread = True
        self.continueToCrawlGamesLock.release()
        if(self.gameThread and self.gameThread.isAlive()):
            self.gameThread.join()
        self.stopGameThread = False
        returnGames = dict(self.finishedGames)
        self.finishedGames = {}
        return returnGames

    def __getPlayersToCrawl(self, startPlayerId, numberOfPlayers):
        crawlChain = []
        players = []
        playerFriends = set()
        firstPlayer = Player()
        firstPlayer.Id = startPlayerId
        if not firstPlayer.Id in self.CrawledPlayers:
            self.CrawledPlayers.add(firstPlayer.Id)
            players.append(firstPlayer)
        crawlChain.append(firstPlayer)
        i = -1
        while len(players) + len(playerFriends) < numberOfPlayers:
            i += 1
            if i < 0:
                break

            currentPlayer = crawlChain[i]
            if not currentPlayer.crawled:
                friendList = self.__getFriendList(currentPlayer.Id)
                if (friendList is not None and "friendslist" in friendList and "friends" in friendList["friendslist"]):
                    for friend in friendList["friendslist"]["friends"]:
                        friendId = friend["steamid"]
                        currentPlayer.Friends.append(friendId)
                        if friendId not in self.CrawledPlayers:
                            friendPlayer = Player()
                            friendPlayer.Id = friendId
                            playerFriends.add(friendPlayer)
                #currentPlayer.Friends = self.__getFriendsListTest(currentPlayer.Id)
                currentPlayer.crawled = True
                currentPlayer.crawlFriends = list(currentPlayer.Friends)
            newPlayerId = None
            while True:
                newPlayerId = None
                if len(currentPlayer.crawlFriends) > 0:
                    newPlayerId = currentPlayer.crawlFriends[randint(
                        0, len(currentPlayer.crawlFriends) - 1)]
                else:
                    break
                currentPlayer.crawlFriends.remove(newPlayerId)
                if newPlayerId not in self.CrawledPlayers:
                    break
            if not newPlayerId is None:  # current player is not a leaf
                self.CrawledPlayers.add(newPlayerId)
                newPlayer = Player()
                newPlayer.Id = newPlayerId
                players.append(newPlayer)
                crawlChain.append(newPlayer)
            else:
                i -= 2
                crawlChain.remove(currentPlayer)
        for playerFriend in playerFriends:
            if playerFriend.Id not in self.CrawledPlayers:
                players.append(playerFriend)
        return players

    def __assemblePlayers(self, *players):
        playerIds = []
        for player in players:
            playerIds.append(player.Id)
        playerInfos = self.__getPlayerSummaries(*playerIds)
        playerBans = self.__getPlayerBans(*playerIds)
        if "players" not in playerBans:
            return
        playerBans = playerBans["players"]
        if (playerInfos is not None and len(playerInfos["response"]["players"]) > 0):
            playerInfos = playerInfos["response"]["players"]
            localPlayers = {}
            for i in range(0, len(playerInfos)):
                playerInfo = playerInfos[i]
                playerId = playerInfo["steamid"]
                player = None
                for localPlayer in players:
                    if localPlayer.Id == playerId:
                        player = localPlayer
                        break

                if "personaname" in playerInfo:
                    player.SteamName = playerInfo["personaname"]
                if "lastlogoff" in playerInfo:
                    player.LastLogOff = playerInfo["lastlogoff"]
                if "realname" in playerInfo:
                    player.RealName = playerInfo["realname"]
                if "communityvisibilitystate" in playerInfo:
                    player.PrivacyState = playerInfo["communityvisibilitystate"]
                if "primaryclanid" in playerInfo:
                    player.PrimaryClanId = playerInfo["primaryclanid"]
                if "timecreated" in playerInfo:
                    player.TimeCreated = playerInfo["timecreated"]
                if "loccountrycode" in playerInfo:
                    player.Country = playerInfo["loccountrycode"]
                if "locstatecode" in playerInfo:
                    player.State = playerInfo["locstatecode"]
                if "loccityid" in playerInfo:
                    player.City = playerInfo["loccityid"]
                if not player.crawled:
                    friendList = self.__getFriendList(player.Id)
                    if (friendList is not None and "friendslist" in friendList and "friends" in friendList["friendslist"]):
                        for friend in friendList["friendslist"]["friends"]:
                            friendId = friend["steamid"]
                            player.Friends.append(friendId)
                ban = None
                for k in range(0, len(playerBans)):
                    if "SteamId" in playerBans[k] and playerBans[k]["SteamId"] == player.Id:
                        ban = playerBans[k]
                        if ("CommunityBanned" in ban and ban["CommunityBanned"] == True) or (
                                "VACBanned" in ban and ban["VACBanned"] == True) or (
                                "NumberOfGameBans" in ban and ban["NumberOfGameBans"] > 0) or (
                                "EconomyBan" in ban and ban["EconomyBan"] != "none"):
                            player.Banned = True
                            if "DaysSinceLastBan" in ban:
                                player.DaysSinceLastBan = ban["DaysSinceLastBan"]
                        break
                if ban is not None:
                    playerBans.remove(ban)
                playerGames = self.__getOwnedGames(player.Id)
                if (playerGames is not None and "response" in playerGames and "games" in playerGames["response"]):
                    playerGames = playerGames["response"]["games"]
                    for playerGame in playerGames:
                        ownedGame = OwnedGame()
                        ownedGame.Id = playerGame["appid"]
                        ownedGame.PlaytimeForever = playerGame["playtime_forever"]
                        if "playtime_2weeks" in playerGame:
                            ownedGame.Playtime2Weeks = playerGame["playtime_2weeks"]
                        if self.crawlPlayerAchievements:
                            playerAchievementsForGame = self.__getPlayerAchievementsForGame(
                                player.Id, ownedGame.Id)
                            if (playerAchievementsForGame is not None and "playerstats" in playerAchievementsForGame and "achievements" in playerAchievementsForGame["playerstats"]):
                                playerAchievementsForGame = playerAchievementsForGame["playerstats"]
                                achievements = playerAchievementsForGame["achievements"]
                                for achievement in achievements:
                                    if achievement["achieved"] == 1:
                                        ownedGame.Achievements.update(
                                            {achievement["apiname"]: achievement["unlocktime"]})
                        player.OwnedGames.append(ownedGame)
                        if not ownedGame.Id in self.CrawledGames:
                            self.__produceGame(ownedGame.Id)
                elif playerGames is None:
                    continue
                self.Players.update({player.Id: player})

    def __shouldContinueToCrawlGames(self):
        result = True
        self.continueToCrawlGamesLock.acquire()
        if self.stopGameThread:
            result = False
        self.continueToCrawlGamesLock.release()
        return result

    def __getGameInfos(self):
        while self.__shouldContinueToCrawlGames() or len(self.gamesToCrawl) > 0:
            localGamesToCrawl = None
            while True:
                self.gameListLock.acquire()
                if len(self.gamesToCrawl) > 0 or not self.__shouldContinueToCrawlGames():
                    localGamesToCrawl = list(self.gamesToCrawl)
                    self.gamesToCrawl = []
                    self.gameListLock.release()
                    break
                else:
                    self.gameListLock.release()
                    time.sleep(10)

            self.__refineGames(*localGamesToCrawl)

    def __refineGames(self, *gamesToCrawl):
        for i in range(0, len(gamesToCrawl)):
            gameId = gamesToCrawl[i]
            gameInfo = self.__getGameDetails(gameId)
            if not gameInfo is None and str(gameId) in gameInfo and "data" in gameInfo[str(gameId)]:
                gameInfo = gameInfo[str(gameId)]["data"]
                if gameInfo is not None:
                    name = ""
                    isFree = None
                    genres = []
                    if "name" in gameInfo:
                        name = gameInfo["name"]
                    if "is_free" in gameInfo:
                        isFree = gameInfo["is_free"]
                    if "genres" in gameInfo:
                        genresList = gameInfo["genres"]
                        for i in range(0, len(genresList)):
                            if "description" in genresList[i]:
                                genres.append(genresList[i]["description"])
                    self.gameListLock.acquire()
                    if not gameId in self.Games:
                        self.__createGame(gameId)
                    self.Games.get(gameId).Name = name
                    self.Games.get(gameId).IsFree = isFree
                    self.Games.get(gameId).Genres = genres
                    self.gameListLock.release()
            self.gameListLock.acquire()
            if gameId in self.Games:
                self.finishedGames.update({gameId: self.Games.get(gameId)})
            self.gameListLock.release()

    def CrawlSpecificGames(self, *gamesToCrawl):
        self.__refineGames(*gamesToCrawl)
        self.gameListLock.acquire()
        returnDict = dict(self.finishedGames)
        self.finishedGames = {}
        self.gameListLock.release()
        return returnDict
