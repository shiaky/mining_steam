#!/usr/bin/env python
import urllib3
import json
from random import randint
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
        self.apiCalls = 0
        self.specialApiCalls = 0
        self.specialApiTime = int(time.time())
        self.firstSpecialApi = True
        self.apiRateLimit = 100000 - 5
        self.specialApiRateLimit = 200 - 5
        self.GamesToSkip = {}
        self.crawlPlayerAchievements = None

    def __executeApiCall(self, call, specialApi=False):
        self.apiCalls += 1
        if self.apiCalls == self.apiRateLimit:
            print("Maximum calls per day reached, discarding all following calls")
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
                    print("Special Api Rate Limit exceeded, sleeping for " +
                          str(sleepTime) + " seconds.")
                    time.sleep(sleepTime)
                    self.specialApiTime = int(time.time())
                    self.specialApiCalls = 0

        r = self.http.request('GET', call)
        resultString = r.data.decode("utf-8")
        result = json.loads(resultString)
        return result, r.status

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
        elif (gameAchievements is None):
            return
        self.Games.update({game.Id: game})

    def CrawlSteam(self, numberOfPlayers, crawlPlayerAchievements):
        self.crawlPlayerAchievements = crawlPlayerAchievements
        self.numberOfPlayers = numberOfPlayers
        while len(self.playerIds) < self.numberOfPlayers:
            id = randint(self.oldestAvailableSteamAccount,
                         self.newestAvailableSteamAccount)
            if not id in self.playerIds:
                self.playerIds.append(id)
        for i in range(0, len(self.playerIds), 100):
            endIndex = (i + 100, len(self.playerIds)
                        )[i + 100 > len(self.playerIds)]
            playerSubList = self.playerIds[i:endIndex]
            self.__assemblePlayers(*playerSubList)
        self.__getGameInfos()
        return self.Players, self.Games

    def __assemblePlayers(self, *playerIds):
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
                player = Player()
                player.Id = playerInfo["steamid"]
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

                friendList = self.__getFriendList(player.Id)
                if (friendList is not None and "friendslist" in friendList and "friends" in friendList["friendslist"]):
                    for friend in friendList["friendslist"]["friends"]:
                        player.Friends.append(friend["steamid"])
                elif friendList is None:
                    continue
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
                        if not ownedGame.Id in self.Games:
                            self.__createGame(ownedGame.Id)
                elif playerGames is None:
                    continue
                self.Players.update({player.Id: player})

    def __getGameInfos(self):
        for gameId in self.Games.keys():
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
                    self.Games.get(gameId).Name = name
                    self.Games.get(gameId).IsFree = isFree
                    self.Games.get(gameId).Genres = genres
