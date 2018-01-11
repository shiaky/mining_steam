#############################################
# generate Genre Distribution as feature
#############################################

import pandas as pd
import sqlite3
import os.path
from multiprocessing.pool import ThreadPool
import numpy as np
import time


# --- config------
sOutputFileName = "feature_genre.csv"
db = "data.db"
lNumberOfPlayersToTest = 10
lNumberOfThreads = 4
lNumberOfGenres = 35
# ----- END -----


# check whether file is existend
bFileExistend = os.path.isfile(sOutputFileName)

# set ThreadPool
oPool = ThreadPool(processes=lNumberOfThreads)

dStart = time.time()
# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(db)
# oGames = pd.read_sql_query("SELECT * FROM games", con)
oPlayers = pd.read_sql_query("SELECT * FROM players", con)
oFriends = pd.read_sql_query("SELECT * FROM friends", con)
oOwnedGames = pd.read_sql_query("SELECT * FROM ownedgames", con)
oGamesGenres = pd.read_sql_query("SELECT * FROM games_genres", con)
con.close()
print("read db: %fs" % (time.time() - dStart))

# --------------------------------------------------------------


def get_Player(lPlayerId):
    return oPlayers[oPlayers["Id"] == lPlayerId]


def get_genres_of_game(lGameId):
    return oGamesGenres[oGamesGenres["game_Id"] == lGameId]["genre_id"].values


def get_playtime_of_game_from_player(lPlayerId, lGameId):
    return oOwnedGames[(oOwnedGames["player_Id"] == lPlayerId) & (oOwnedGames["game_Id"] == lGameId)]["PlaytimeForever"].values[0]


def get_genre_dist_and_totalplaytime_of_player(lPlayerId):
    aGenreDist = np.zeros(lNumberOfGenres)
    aGames = get_owned_games(lPlayerId)
    # print("get genres of %i games" % (len(aGames)))
    lTotalPlaytime = 0
    for lGameId in aGames:
        aGenreIdx = get_genres_of_game(lGameId)
        lPlaytime = get_playtime_of_game_from_player(lPlayerId, lGameId)
        # handle the cases that the game is no game but a video and has no
        # genre or that the game was never played
        if len(aGenreIdx) == 0 or lPlaytime == 0:
            continue
        lTotalPlaytime += lPlaytime
        dSingleGenrePlaytime = lPlaytime / len(aGenreIdx)
        # add playtimes to genres
        for lGenreIdx in aGenreIdx:
            aGenreDist[lGenreIdx - 1] += dSingleGenrePlaytime
    aResult = aGenreDist / aGenreDist.sum() if aGenreDist.sum() > 0 else None
    return aResult, lTotalPlaytime


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
    dicFriendsGameConnectivity = {"playerId": [], "playerGenreDistribution": [], "mainGenre": [], "mainGenrePercentage": [], "meanFriendsGenreDistribution": [], "friendsMainGenre": [], "friendsMainGenrePercentage": [
    ], "palyerTotalPlaytime": [], "friendsTotalPlaytime": [], "numberOfPlayersGenres": [], "numberOfFriendsTotal": [], "numberOfFriendsConsidered": [], "numberOfFriendsWithoutPlayedGames": []}

    for lExploredPlayerId in aPlayersToExplore:
        dStart = time.time()
        aFriends = get_player_friends_crawled(lExploredPlayerId)
        lNumberOfFriends = len(aFriends)
        lNumberOfFriendsConsidered = lNumberOfFriends
        lNumberOfFriendsWithoutPlayedGames = 0
        # handle if no friends
        if lNumberOfFriends == 0:
            print("player has no crawled friends ... skip player")
            continue
        aPlayerGenreDistribution, lPlayerTotalPlaytime = get_genre_dist_and_totalplaytime_of_player(
            lExploredPlayerId)
        # handle if player has has no played games
        if aPlayerGenreDistribution is None:
            print("player has no played games .. skip player")
            continue
        lMainGenre = aPlayerGenreDistribution.argmax() + 1
        dMainGenrePercentage = aPlayerGenreDistribution.max()
        aMeanFriendsGenreDistribution = np.zeros(lNumberOfGenres)
        lFriendsTotalPlaytime = 0
        for lFriendId in aFriends:
            aFriendGenreDistribution, lFriendPlaytime = get_genre_dist_and_totalplaytime_of_player(
                lFriendId)
            # handle if friend has no genre Distribution
            if aFriendGenreDistribution is not None:
                aMeanFriendsGenreDistribution += aFriendGenreDistribution
                lFriendsTotalPlaytime += lFriendPlaytime
            else:
                lNumberOfFriendsConsidered -= 1
                lNumberOfFriendsWithoutPlayedGames += 1
                print("one friend has no played games")
        # handle if no friends have played games
        if aMeanFriendsGenreDistribution.sum() == 0:
            print("no friend has played games ... skip player")
            continue

        # normalize to mean
        aMeanFriendsGenreDistribution /= lNumberOfFriendsConsidered
        # get index of main genre
        # +1 because genres start with 1
        lFriendsMainGenre = aMeanFriendsGenreDistribution.argmax() + 1
        dFriendsMainGenrePercentage = aMeanFriendsGenreDistribution.max()
        lNumberOfPlayersGenres = np.count_nonzero(aPlayerGenreDistribution)
        # add data to dataframe
        dicFriendsGameConnectivity["playerId"].append(lExploredPlayerId)
        dicFriendsGameConnectivity["playerGenreDistribution"].append(
            aPlayerGenreDistribution)
        dicFriendsGameConnectivity["mainGenre"].append(lMainGenre)
        dicFriendsGameConnectivity["mainGenrePercentage"].append(
            dMainGenrePercentage)

        dicFriendsGameConnectivity["meanFriendsGenreDistribution"].append(
            aMeanFriendsGenreDistribution)
        dicFriendsGameConnectivity["friendsMainGenre"].append(
            lFriendsMainGenre)
        dicFriendsGameConnectivity["friendsMainGenrePercentage"].append(
            dFriendsMainGenrePercentage)
        dicFriendsGameConnectivity["palyerTotalPlaytime"].append(
            lPlayerTotalPlaytime)
        dicFriendsGameConnectivity["friendsTotalPlaytime"].append(
            lFriendsTotalPlaytime)
        dicFriendsGameConnectivity["numberOfPlayersGenres"].append(
            lNumberOfPlayersGenres)
        dicFriendsGameConnectivity["numberOfFriendsTotal"].append(
            lNumberOfFriends)
        dicFriendsGameConnectivity["numberOfFriendsConsidered"].append(
            lNumberOfFriendsConsidered)
        dicFriendsGameConnectivity["numberOfFriendsWithoutPlayedGames"].append(
            lNumberOfFriendsWithoutPlayedGames)

        print("%f, player %i, mg: %i, fg: %i, #f: %i, #fwpg: %i" %
              ((time.time() - dStart), lExploredPlayerId, lMainGenre,  lFriendsMainGenre, lNumberOfFriends, lNumberOfFriendsWithoutPlayedGames))
    return dicFriendsGameConnectivity


# ----- main program ---------

if __name__ == "__main__":
    dicFriendsGameConnectivity = {"playerId": [], "playerGenreDistribution": [], "mainGenre": [], "mainGenrePercentage": [], "meanFriendsGenreDistribution": [], "friendsMainGenre": [], "friendsMainGenrePercentage": [
    ], "palyerTotalPlaytime": [], "friendsTotalPlaytime": [], "numberOfPlayersGenres": [], "numberOfFriendsTotal": [], "numberOfFriendsConsidered": [], "numberOfFriendsWithoutPlayedGames": []}
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
        dicFriendsGameConnectivity["meanFriendsGenreDistribution"].extend(
            dicResult["meanFriendsGenreDistribution"])
        dicFriendsGameConnectivity["playerGenreDistribution"].extend(
            dicResult["playerGenreDistribution"])
        dicFriendsGameConnectivity["mainGenre"].extend(
            dicResult["mainGenre"])
        dicFriendsGameConnectivity["mainGenrePercentage"].extend(
            dicResult["mainGenrePercentage"])
        dicFriendsGameConnectivity["friendsMainGenre"].extend(
            dicResult["friendsMainGenre"])
        dicFriendsGameConnectivity["friendsMainGenrePercentage"].extend(
            dicResult["friendsMainGenrePercentage"])
        dicFriendsGameConnectivity["palyerTotalPlaytime"].extend(
            dicResult["palyerTotalPlaytime"])
        dicFriendsGameConnectivity["friendsTotalPlaytime"].extend(
            dicResult["friendsTotalPlaytime"])
        dicFriendsGameConnectivity["numberOfPlayersGenres"].extend(
            dicResult["numberOfPlayersGenres"])
        dicFriendsGameConnectivity["numberOfFriendsTotal"].extend(
            dicResult["numberOfFriendsTotal"])
        dicFriendsGameConnectivity["numberOfFriendsConsidered"].extend(
            dicResult["numberOfFriendsConsidered"])
        dicFriendsGameConnectivity["numberOfFriendsWithoutPlayedGames"].extend(
            dicResult["numberOfFriendsWithoutPlayedGames"])

    oExportDataFrame = pd.DataFrame(dicFriendsGameConnectivity)

    #  add Country, State, City, Banned, DaysSinceLastBan
    oExportDataFrame = oExportDataFrame.merge(oPlayers.loc[oPlayers["Id"].isin(oExportDataFrame["playerId"].values)][[
        "Id", "Country", "State", "City", "DaysSinceLastBan", "Banned"]], left_on="playerId", right_on="Id")

    oExportDataFrame = oExportDataFrame.drop("Id", axis=1)
    # append data if file already existend
    if bFileExistend:
        #oExportDataFrame.to_csv(sOutputFileName, mode='a', header=False)
        oExistingDataFrame = pd.read_csv(sOutputFileName)
        oExportDataFrame = pd.concat(
            [oExistingDataFrame, oExportDataFrame], ignore_index=True)

    oExportDataFrame.to_csv(sOutputFileName, index=False)


# ----------------------------------------------------------------------
