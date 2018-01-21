import pandas as pd
import numpy as np
# import sqlite3 as sql
from SteamCrawler import Game, Player, OwnedGame
# from SteamDbStore import SteamDbStore
import json
from random import shuffle
import time
from sklearn.neural_network import MLPClassifier
import math

# conn = sql.connect("C:\\Users\\Alexander\\Desktop\\Dektop\\Uni\\data_01-12-17_clean.db")
# playerDF = pd.read_sql_query("select * from players limit 10", conn)

class MainPlayerTuple(object):
    mainPlayer = None
    friends = list()

    def __init__(self, mainP, fr):
        self.mainPlayer = mainP
        self.friends = list(fr)


class DataClass(object):
    conn = None
    cursor = None
    playerDF = None
    ownedGamesDF = None
    gamesDF = None
    gamesGenresDF = None
    friendsDF = None

    def __init__(self):
        #self.conn = sql.connect("C:\\Users\\Alexander\\Desktop\\Dektop\\Uni\\data_01-12-17_clean.db")
        #self.playerDF = pd.read_sql_query("select * from players", conn)
        #self.ownedGamesDF = pd.read_sql_query("select * from ownedgames", conn)
        #self.friendsDF = pd.read_sql_query("select * from friends", conn)
        #self.gamesDF = pd.read_sql_query("select * from games", conn)
        #self.gamesGenresDF = pd.read_sql_query("select * from games_genres", conn)
        #self.cursor = conn.cursor()
        pass

    def getGames(self, topGames):
        gamesList = dict()
        for index, row in self.gamesDF.iterrows():
            game = Game()
            game.Id = int(row["Id"])
            if str(game.Id) not in topGames:
                continue
            game.Name = row["Name"]
            game.Genres = list()
            genreDF = self.gamesGenresDF[self.gamesGenresDF["game_Id"] == game.Id]
            for index, row in genreDF.iterrows():
                game.Genres.append(row["genre_id"])
            gamesList.update({str(game.Id) : game})
        return gamesList

    def getPlayerCreatedAndLogOff(self, player):
        df = self.playerDF[self.playerDF['Id'] == player.Id]
        for index, row in df.iterrows():
            player.TimeCreated = row["TimeCreated"]
            player.LastLogOff = row["LastLogOff"]


    def getPlayer(self, id):
        p = Player()
        #df = pd.read_sql_query("select * from players where Id == " + str(id), conn)
        df = self.playerDF[self.playerDF['Id'] == id]
        if df.empty:
            return None
        p.Id = df.iat[0, 0]
        #df = pd.read_sql_query("select * from ownedgames where player_Id == " +str(p.Id), conn)
        df = self.ownedGamesDF[self.ownedGamesDF['player_Id'] == p.Id]
        for index, row in df.iterrows():
            og = OwnedGame()
            og.Id = row['game_Id']
            og.PlaytimeForever = row['PlaytimeForever']
            p.OwnedGames.append(og)
        #df = pd.read_sql_query("select * from friends where player_Id1 == " + str(p.Id) + " or player_Id2 == " + str(p.Id), conn)
        df = self.friendsDF[(self.friendsDF['player_Id1'] == id)  | (self.friendsDF['player_Id2'] == id)]
        for index, row in df.iterrows():
            if row["player_Id1"] == p.Id:
                p.Friends.append(row["player_Id2"])
            elif row["player_Id2"] == p.Id:
                p.Friends.append(row["player_Id1"])
        return p

    mainsss = set()
    def getFirstMainPlayer(self, playerId):
        potentialMainPlayer = self.getPlayer(playerId)
        friendsList = list()
        if potentialMainPlayer is None:
            return None
        for friend in potentialMainPlayer.Friends:
            friendPlayer = self.getPlayer(friend)
            if friendPlayer is not None:
                friendsList.append(friendPlayer)
        if float(len(potentialMainPlayer.Friends))*0.8 <= len(friendsList):
            self.mainsss.update({str(potentialMainPlayer.Id)})
            return MainPlayerTuple(potentialMainPlayer, friendsList)
        return None

    def findMainPlayer(self, friends):
        friends = list(friends)
        for friend in friends:
            ff = friend.Friends
            friendsList = list()
            for fff in ff:
                friendPlayer = self.getPlayer(fff)
                if friendPlayer is not None:
                    friendsList.append(friendPlayer)
            if float(len(friend.Friends)) * 0.8 >= len(friendsList) and not str(friend.Id) in self.mainsss:
                self.mainsss.update({str(friend.Id)})
                result = MainPlayerTuple(friend, friendsList)
                return result

    def getMainPlayers(self, count, startId):
        mainPlayerTupleList = list()
        currentId = startId
        main = self.getFirstMainPlayer(currentId)
        if main is None:
            raise Exception("First player")
        mainPlayerTupleList.append(main)
        while len(mainPlayerTupleList) < count:
            mainPlayer = self.findMainPlayer(main.friends)
            if not mainPlayer is None:
                mainPlayerTupleList.append(mainPlayer)
                main = mainPlayer
            else:
                return mainPlayerTupleList
        return mainPlayerTupleList

    def newGetMainPlayers(self, count):
        tupleList = list()
        playerIdDf = self.playerDF["Id"]
        playerList = list(playerIdDf)
        shuffle(playerList)
        for row in playerList:
            potentialMain = self.getPlayer(int(row))
            if self.calcAcumulatedGameTime(potentialMain) < 600:
                continue
            friendList = list()
            for friendId in potentialMain.Friends:
                friend = self.getPlayer(int(friendId))
                if not friend is None:
                    friendList.append(friend)
            if float(len(potentialMain.Friends)) * 0.8 <= len(friendList) and len(potentialMain.Friends) > 5:
                newTuple = MainPlayerTuple(potentialMain, friendList)
                tupleList.append(newTuple)
                if len(tupleList) >= count:
                    break
        return tupleList

    def calcAcumulatedGameTime(self, player):
        cumulatedGameTimeOfPlayer = 0
        for game in player.OwnedGames:
            cumulatedGameTimeOfPlayer += int(game.PlaytimeForever)
        return cumulatedGameTimeOfPlayer




    def safePlayer(self, p):
        playerDict = {}
        friendsList = list()
        for f in p.Friends:
            friendsList.append(str(f))
        playerDict.update({"friends" : friendsList})
        gamesList = list()
        for game in p.OwnedGames:
            data = {str(game.Id) : str(game.PlaytimeForever)}
            gamesList.append(data)
        playerDict.update({"ownedGames" : gamesList})
        if p.SteamName is None:
            p.SteamName = np.array([])
        vectorList = p.SteamName.tolist()
        playerDict.update({"genreVector" : vectorList})
        playerDict.update({"Id": str(p.Id)})
        if p.PrimaryClanId is None:
            p.PrimaryClanId = 0.
        playerDict.update(({"friendConnectivity" : p.PrimaryClanId}))
        playerDict.update(({"timeCreated": p.TimeCreated}))
        playerDict.update(({"lastLogOff": p.LastLogOff}))
        return playerDict

    def safeAll(self ,tupleList):
        tupleList = list(tupleList)
        resultList = list()
        for tuple in tupleList:
            friendsList = list()
            for friend in tuple.friends:
                friendString = self.safePlayer(friend)
                friendsList.append(friendString)
            main = self.safePlayer(tuple.mainPlayer)
            someDict = {}
            someDict.update({"mainPlayer" : main})
            someDict.update({"friends" : friendsList})
            resultList.append(someDict)

        with open('C:\\Users\\Alexander\\Desktop\\Dektop\\Uni\\fileSave.txt', 'w') as fp:
            json.dump(resultList, fp)

    def loadJson(self, jsonLocation):
        mainPlayerTupleList = list()
        with open(jsonLocation) as fp:
            data = json.load(fp)
            for entry in data:
                mainPlayerDict = entry["mainPlayer"]
                mainPlayer = self.constructPlayer(mainPlayerDict)
                friendsList = list()
                friendsDict = entry["friends"]
                for friend in friendsDict:
                    friendPlayer = self.constructPlayer(friend)
                    friendsList.append(friendPlayer)
                tuple = MainPlayerTuple(mainPlayer, friendsList)
                mainPlayerTupleList.append(tuple)
        return mainPlayerTupleList




    def constructPlayer(self, playerDict):
        player = Player()
        player.Id = int(playerDict["Id"])
        player.TimeCreated=float(playerDict["timeCreated"])
        player.LastLogOff = float(playerDict["lastLogOff"])
        player.OwnedGames = list()
        player.Friends = list()
        for game in playerDict["ownedGames"]:
            g = list(game.keys())[0]
            og = OwnedGame()
            og.Id = int(g)
            og.PlaytimeForever = int(game[g])
            player.OwnedGames.append(og)
        for friend in playerDict["friends"]:
            player.Friends.append(int(friend))
        genreVectorList = list()
        for entry in playerDict["genreVector"]:
            genreVectorList.append(float(entry))
        player.PrimaryClanId = playerDict["friendConnectivity"]
        genreVector = np.asarray(genreVectorList)
        player.SteamName = genreVector
        return player

    def reduceGames(self, player, gamesSet):
        newOwnedGames = list()
        for ownedGame in player.OwnedGames:
            if str(ownedGame.Id) in gamesSet:
                newOwnedGames.append(ownedGame)
        player.OwnedGames = newOwnedGames

    def calcGenreArray(self, player, gamesDict):
        genreVector = np.array([0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.])
        cumulatedGameTimeOfPlayer = 0
        for game in player.OwnedGames:
            cumulatedGameTimeOfPlayer += int(game.PlaytimeForever)
        for game in player.OwnedGames:
            gamePlayTime = int(game.PlaytimeForever)
            multiplier = 0
            if not (cumulatedGameTimeOfPlayer == 0 or gamePlayTime == 0):
                multiplier = float(gamePlayTime)/float(cumulatedGameTimeOfPlayer)
            genreList = gamesDict[str(game.Id)].Genres
            for genre in genreList:
                genreMultiplier = 1./float(len(genreList))
                genreVector[int(genre) - 1] += genreMultiplier*multiplier
        genreVector = genreVector/np.linalg.norm(genreVector)
        player.SteamName = genreVector

    def averageArrays(self, *arrays):
        arrays = list(arrays)
        startArray = np.array(arrays[0])
        for i in range(0, len(startArray)):
            startArray[i] = 0.
        for array in arrays:
            if not np.isnan(array).any():
                startArray += array
        startArray = startArray/len(arrays)
        startArray = startArray / np.linalg.norm(startArray)
        return startArray

    def getBiggestIndexFromArray(self, array):
        array = list(array)
        currIndex = -1
        index = 0
        value = 0.
        for entry in array:
            currIndex+=1
            if float(entry) > value:
                index = currIndex
                value = float(entry)
        return index

    def calcFriendConnectivity(self, tuple):
        listOfFriends = set(tuple.mainPlayer.Friends)
        friendConnectivity = 0.
        for friend in tuple.friends:
            knownFriends = 0
            listOfFriendsFriends = set(friend.Friends)
            intersection = listOfFriends.intersection(listOfFriendsFriends)
            knownFriends = len(intersection)
            localFriendConnectivity = knownFriends/(len(listOfFriends) -1)
            friendConnectivity += localFriendConnectivity
        friendConnectivity /= len(listOfFriends)
        tuple.mainPlayer.PrimaryClanId = friendConnectivity

    def friendsOwnGame(self, friends, gameId):
        for friend in friends:
            for game in friend.OwnedGames:
                if str(game.Id) == str(gameId):
                    return True
        return False

    def getMostPlayedGameOfFriendsInPercent(self, friends):
        games = dict()
        completePlaytime = 0.
        for friend in friends:
            for game in friend.OwnedGames:
                if str(game.Id) not in games:
                    gameTime = game.PlaytimeForever
                    games.update({str(game.Id) : gameTime})
                    completePlaytime += gameTime
                else:
                    games[str(game.Id)] += game.PlaytimeForever
                    completePlaytime += game.PlaytimeForever
        mostPlayedGame = ""
        mostPlayedGameTime = 0.
        for game in games:
            if int(games[game]) > mostPlayedGameTime:
                mostPlayedGameTime = int(games[game])
                mostPlayedGame = int(game)
        gameTimePercent = mostPlayedGameTime/completePlaytime
        return (mostPlayedGame, gameTimePercent)

    def calcCompleteGameTime(self, player):
        gameTime = 0
        for game in player.OwnedGames:
            gameTime+= game.PlaytimeForever
        return gameTime

    def calcNumberOfPlayedGames(self, player):
        nrOfGames = 0
        for game in player.OwnedGames:
            if game.PlaytimeForever > 0:
                nrOfGames +=1
        return nrOfGames

    def getListLimits(self, someList):
        someList = list(someList)
        upperLimit = someList[int(len(someList) * 0.97)]
        lowerLimit = someList[int(len(someList) * 0.03)]
        return (lowerLimit, upperLimit)

    def classifyPlayer(self, playerTime):
        casualLimit = 1500*60

        if playerTime <= casualLimit:
            return 0
        return 1




dataTool = DataClass()

playerTupleList = dataTool.loadJson("fileSave_big.json")

pdAnalysisData = pd.DataFrame(columns=['id','lastLogOff','timeCreated','accountAge', 'accountAgePersonal' , 'nrOfGamesOwned', 'totalNumberOfGamesPlayedFriends', 'meanNumberOfPGameslayedFriends', 'nrOfGamesPlayed', 'totalPlaytime', 'nrOfFriends', 'totalPlaytimeFriends', 'meanPlaytimeFriends', 'totalNrOfGamesOwnedFriends', 'meanNrOfGamesOwnedFriends', 'totalAccountAgeFriends', 'meanAccountAgeFriends', 'totalAccountAgeFriendsPersonal', 'meanAccountAgeFriendsPersonal'])

# get global lastLogOff
globalMaxLastLogOff = 0
for playerTuple in playerTupleList:
    if playerTuple.mainPlayer.LastLogOff > globalMaxLastLogOff:
        globalMaxLastLogOff = playerTuple.mainPlayer.LastLogOff
    for friend in playerTuple.friends:
        if friend.LastLogOff > globalMaxLastLogOff:
            globalMaxLastLogOff = friend.LastLogOff

# calc data for every player
for playerTuple in playerTupleList:
    mainPlayer = playerTuple.mainPlayer
    friends = playerTuple.friends

    # do your stuff here
    idd = mainPlayer.Id
    lastLogOff = mainPlayer.LastLogOff
    timeCreated = mainPlayer.TimeCreated
    nrOfGamesOwned = len(mainPlayer.OwnedGames)
    nrOfGamesPlayed = dataTool.calcNumberOfPlayedGames(mainPlayer)
    accountAge = globalMaxLastLogOff - timeCreated
    accountAgePersonal = lastLogOff - timeCreated
    totalPlaytime = dataTool.calcCompleteGameTime(mainPlayer)
    nrOfFriends = len(friends)
    totalPlaytimeFriends = 0
    totalNrOfGamesOwnedFriends = 0
    totalAccountAgeFriends = 0
    totalAccountAgeFriendsPersonal = 0
    totalNumberOfGamesPlayedFriends = 0
    for friend in friends:
        totalPlaytimeFriends += dataTool.calcCompleteGameTime(friend)
        totalNrOfGamesOwnedFriends += len(friend.OwnedGames)
        totalNumberOfGamesPlayedFriends += dataTool.calcNumberOfPlayedGames(friend)
        totalAccountAgeFriends += globalMaxLastLogOff - friend.TimeCreated
        totalAccountAgeFriendsPersonal += friend.LastLogOff - friend.TimeCreated
    meanPlaytimeFriends = totalPlaytimeFriends / nrOfFriends
    meanNrOfGamesOwnedFriends = totalNrOfGamesOwnedFriends / nrOfFriends
    meanNumberOfGamesPlayedFriends = totalNumberOfGamesPlayedFriends / nrOfFriends
    meanAccountAgeFriends = totalAccountAgeFriends / nrOfFriends
    meanAccountAgeFriendsPersonal = totalAccountAgeFriendsPersonal / nrOfFriends


    pdAnalysisData = pdAnalysisData.append({
            'id': idd,
            'lastLogOff': lastLogOff,
            'timeCreated': timeCreated,
            'accountAge': accountAge,
            'accountAgePersonal': accountAgePersonal,
            'nrOfGamesOwned': nrOfGamesOwned,
            'nrOfGamesPlayed': nrOfGamesPlayed,
            'totalPlaytime': totalPlaytime,
            'nrOfFriends': nrOfFriends,
            'totalPlaytimeFriends': totalPlaytimeFriends,
            'meanPlaytimeFriends': meanPlaytimeFriends,
            'totalNrOfGamesOwnedFriends': totalNrOfGamesOwnedFriends,
            'meanNrOfGamesOwnedFriends': meanNrOfGamesOwnedFriends,
            'totalNumberOfGamesPlayedFriends' : totalNumberOfGamesPlayedFriends,
            'meanNumberOfPGameslayedFriends': meanNumberOfGamesPlayedFriends,
            'totalAccountAgeFriends': totalAccountAgeFriends,
            'meanAccountAgeFriends': meanAccountAgeFriends,
            'totalAccountAgeFriendsPersonal': totalAccountAgeFriendsPersonal,
            'meanAccountAgeFriendsPersonal': meanAccountAgeFriendsPersonal
            }, ignore_index=True)

    pdAnalysisData.to_csv("plot_data_big.csv", index=False)
