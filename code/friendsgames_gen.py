#import matplotlib.pyplot as plt
import pandas as pd
#import seaborn as sns
import sqlite3
import json
import os.path
from multiprocessing.pool import ThreadPool
import numpy as np

# Import config
with open("config.json", "r") as json_file:
    config = json.load(json_file)


# --- config------
sOutputFileName = "friendsgames.csv"
lNumberOfPlayersToTest = 4000
lNumberOfThreads = 3
# ----- END -----


db = config["db"]
# check whether file is existend
bFileExistend = os.path.isfile(sOutputFileName)

# set ThreadPool
oPool = ThreadPool(processes=lNumberOfThreads)


# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(db)
oGames = pd.read_sql_query("SELECT * FROM games", con)
oPlayers = pd.read_sql_query("SELECT * FROM players", con)
oFriends = pd.read_sql_query("SELECT * FROM friends", con)
oOwnedGames = pd.read_sql_query("SELECT * FROM ownedgames", con)
con.close()

# 1 . freundekonnektivität -> % der Spiele des unters. Spielers die mindestens einer seiner Freunde besitzt
#  * nur 1500 häufigsten?
#  * zahl zwischen 0 und 1
#  * schaue alle spiele an die er besitzt
#  * alle spiel die die freunde besitzen
#  * 1 ist alle spiele des untersuchten spielers
#  * alle rausfiltern, die nicht in der db als player sind


def get_Player(lPlayerId):
    return oPlayers[oPlayers["Id"] == lPlayerId]


def get_player_friends(lPlayerId):
    oTmpFriends = oFriends[(oFriends["player_Id1"] == lPlayerId) | (
        oFriends["player_Id2"] == lPlayerId)]
    return [p1 if p1 != lPlayerId else p2 for p1, p2 in oTmpFriends.values]


def get_owned_games_as_set(lPlayerId):
    return set(oOwnedGames[oOwnedGames["player_Id"] == lPlayerId]["game_Id"].values)


def explore_list_of_players(aPlayersToExplore):
    dicFriendsGameConnectivity = {"playerId": [],
                                  "commonGames": [], "numberOfGames": [], "numberOfFriends": []}

    for lExploredPlayerId in aPlayersToExplore:
        #lExploredPlayerId = 76561198063135040
        aPlayerFriends = get_player_friends(lExploredPlayerId)
        lNumberOfFriends = len(aPlayerFriends)
        sePlayerGames = get_owned_games_as_set(lExploredPlayerId)
        lExploredPlayerGameCount = len(sePlayerGames)
        # handle case that player has 0 games
        if lExploredPlayerGameCount == 0:
            continue
        seFriendsGames = set()
        for lFriendPlayerId in aPlayerFriends:
            seGames = get_owned_games_as_set(lFriendPlayerId)
            seFriendsGames = seFriendsGames | seGames
        dPercentOfCommonGames = len(
            seFriendsGames & sePlayerGames) / lExploredPlayerGameCount
        # add data to dataframe
        dicFriendsGameConnectivity["playerId"].append(lExploredPlayerId)
        dicFriendsGameConnectivity["commonGames"].append(dPercentOfCommonGames)
        dicFriendsGameConnectivity["numberOfGames"].append(
            lExploredPlayerGameCount)
        dicFriendsGameConnectivity["numberOfFriends"].append(lNumberOfFriends)

        print("player %i, gamesCount %i, pCommon: %f, nOfFriends: %i" %
              (lExploredPlayerId, lExploredPlayerGameCount, dPercentOfCommonGames, lNumberOfFriends))
    return dicFriendsGameConnectivity


# 1. get list of players to test
# 2. for each: get games set and calculate number of games
# 3. get list of friends
# 4. get games of friends if friends in db
# 5. calculate number of intersections
dicFriendsGameConnectivity = {"playerId": [],
                              "commonGames": [], "numberOfGames": [], "numberOfFriends": []}
aPlayersToExploreFulltake = oPlayers.sample(
    n=lNumberOfPlayersToTest, replace=False)["Id"].values

aPlayersToExploreSplit = np.array_split(
    aPlayersToExploreFulltake, lNumberOfThreads)

aProcesses = []
for aPlayersToExplore in aPlayersToExploreSplit:
    aProcesses.append(oPool.apply_async(
        explore_list_of_players, (aPlayersToExplore,)))

for i in range(lNumberOfThreads):
    dicResult = aProcesses[i].get()
    dicFriendsGameConnectivity["playerId"].extend(dicResult["playerId"])
    dicFriendsGameConnectivity["commonGames"].extend(dicResult["commonGames"])
    dicFriendsGameConnectivity["numberOfGames"].extend(
        dicResult["numberOfGames"])
    dicFriendsGameConnectivity["numberOfFriends"].extend(
        dicResult["numberOfFriends"])

oExportDataFrame = pd.DataFrame(dicFriendsGameConnectivity)
# append data if file already existend
if bFileExistend:
    oExportDataFrame.to_csv(sOutputFileName, mode='a', header=False)
else:
    oExportDataFrame.to_csv(sOutputFileName)


# ----------------------------------------------------------------------
