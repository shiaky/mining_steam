# import matplotlib.pyplot as plt
import pandas as pd
# import seaborn as sns
import sqlite3
import json
import os.path
from multiprocessing.pool import ThreadPool
import numpy as np
import math

# Import config
with open("config.json", "r") as json_file:
    config = json.load(json_file)


# --- config------
sOutputFileName = "genredist.csv"
lNumberOfPlayersToTest = 6
lNumberOfThreads = 3
lNumberOfGenres = 35
# ----- END -----


db = config["db"]
# check whether file is existend
bFileExistend = os.path.isfile(sOutputFileName)

# set ThreadPool
oPool = ThreadPool(processes=lNumberOfThreads)


# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(db)
#oGames = pd.read_sql_query("SELECT * FROM games", con)
oPlayers = pd.read_sql_query("SELECT * FROM players", con)
oFriends = pd.read_sql_query("SELECT * FROM friends", con)
oOwnedGames = pd.read_sql_query("SELECT * FROM ownedgames", con)
oGamesGenres = pd.read_sql_query("SELECT * FROM games_genres", con)
con.close()

# 5. Distanz Genre-Distribution des unters. Spielers zu den Genre-dist. der Freunde -> Freundes-Konnektivität
#  * genre distribution (vektor der Genres anhand der spielzeit des Spiels), auf 1 normalisiert
#  * vektordistanz im raum


def get_Player(lPlayerId):
    return oPlayers[oPlayers["Id"] == lPlayerId]


def get_genres_of_game(lGameId):
    return oGamesGenres[oGamesGenres["game_Id"] == lGameId]["genre_id"].values


def get_playtime_of_game_from_player(lPlayerId, lGameId):
    return oOwnedGames[(oOwnedGames["player_Id"] == lPlayerId) & (oOwnedGames["game_Id"] == lGameId)]["PlaytimeForever"].values[0]


def get_genre_dist_of_player(lPlayerId):
    aGenreDist = np.zeros(lNumberOfGenres)
    aGames = get_owned_games(lPlayerId)
    for lGameId in aGames:
        aGenreIdx = get_genres_of_game(lGameId)
        dPlaytime = get_playtime_of_game_from_player(lPlayerId, lGameId)
        # handle the cases that the game is no game but a video and has no
        # genre or that the game was never played
        if len(aGenreIdx) == 0 or dPlaytime == 0:
            continue
        dSingleGenrePlaytime = dPlaytime / len(aGenreIdx)
        # add playtimes to genres
        for lGenreIdx in aGenreIdx:
            aGenreDist[lGenreIdx - 1] += dSingleGenrePlaytime
    # return normalized vector
    return aGenreDist / np.linalg.norm(aGenreDist)


def calculate_euclidean_dist(aVec1, aVec2):
    aVec1 = np.array(aVec1)
    aVec2 = np.array(aVec2)
    return np.linalg.norm(aVec1 - aVec2) / math.sqrt(2)


def get_player_friends(lPlayerId):
    oTmpFriends = oFriends[(oFriends["player_Id1"] == lPlayerId) | (
        oFriends["player_Id2"] == lPlayerId)]
    return [p1 if p1 != lPlayerId else p2 for p1, p2 in oTmpFriends.values]


def get_player_friends_crawled(lPlayerId):
    """ get the friends existing in the players table only """
    aPlayerFriends = get_player_friends(lPlayerId)

    # filter friends that are not in db
    for lFriendPlayerId in aPlayerFriends:
        if lFriendPlayerId not in oPlayers["Id"]:
            aPlayerFriends.remove(lFriendPlayerId)
    return aPlayerFriends


def get_owned_games(lPlayerId):
    return oOwnedGames[oOwnedGames["player_Id"] == lPlayerId]["game_Id"].values


def explore_list_of_players(aPlayersToExplore):
    dicFriendsGameConnectivity = {"playerId": [],
                                  "meanGenreDistributionDistance": [], "numberOfGenres": [], "numberOfFriends": []}

    for lExploredPlayerId in aPlayersToExplore:
        aFriends = get_player_friends_crawled(lExploredPlayerId)
        lNumberOfFriends = len(aFriends)
        # handle if no friends
        if lNumberOfFriends == 0:
            continue
        aPlayerGenreDistribution = get_genre_dist_of_player(lExploredPlayerId)
        aMeanFriendsGenreDistribution = np.zeros(lNumberOfGenres)
        for lFriendId in aFriends:
            aFriendGenreDistribution = get_genre_dist_of_player(lFriendId)
            aMeanFriendsGenreDistribution += aFriendGenreDistribution
        # normalize to mean
        aMeanFriendsGenreDistribution /= lNumberOfFriends
        dMeanGenreDistributionDistance = calculate_euclidean_dist(
            aPlayerGenreDistribution, aMeanFriendsGenreDistribution)
        lNumberOfPlayersGenres = np.count_nonzero(aPlayerGenreDistribution)

        # add data to dataframe
        dicFriendsGameConnectivity["playerId"].append(lExploredPlayerId)
        dicFriendsGameConnectivity["meanGenreDistributionDistance"].append(
            dMeanGenreDistributionDistance)
        dicFriendsGameConnectivity["numberOfGenres"].append(
            lNumberOfPlayersGenres)
        dicFriendsGameConnectivity["numberOfFriends"].append(lNumberOfFriends)

        print("player %i, meanGenreDistributionDistance: %f, noOfGenres: %i, nOfFriends: %i" %
              (lExploredPlayerId, dMeanGenreDistributionDistance, lNumberOfPlayersGenres, lNumberOfFriends))
    return dicFriendsGameConnectivity


# ----- main program ---------


dicFriendsGameConnectivity = {"playerId": [], "meanGenreDistributionDistance": [
], "numberOfGenres": [], "numberOfFriends": []}
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
    dicFriendsGameConnectivity["meanGenreDistributionDistance"].extend(
        dicResult["meanGenreDistributionDistance"])
    dicFriendsGameConnectivity["numberOfGenres"].extend(
        dicResult["numberOfGenres"])
    dicFriendsGameConnectivity["numberOfFriends"].extend(
        dicResult["numberOfFriends"])

oExportDataFrame = pd.DataFrame(dicFriendsGameConnectivity)
# append data if file already existend
if bFileExistend:
    oExportDataFrame.to_csv(sOutputFileName, mode='a', header=False)
else:
    oExportDataFrame.to_csv(sOutputFileName)


# ----------------------------------------------------------------------
