# import matplotlib.pyplot as plt
import pandas as pd
# import seaborn as sns
import sqlite3
import json
import os.path
from multiprocessing.pool import ThreadPool
import numpy as np

# Import config
with open("config.json", "r") as json_file:
    config = json.load(json_file)


# --- config------
sOutputFileName = "friendscon.csv"
lNumberOfPlayersToTest = 15000
lNumberOfThreads = 3
# ----- END -----


db = config["db"]
# check whether file is existend
bFileExistend = os.path.isfile(sOutputFileName)

# set ThreadPool
oPool = ThreadPool(processes=lNumberOfThreads)


# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(db)
# oGames = pd.read_sql_query("SELECT * FROM games", con)
oPlayers = pd.read_sql_query("SELECT * FROM players", con)
oFriends = pd.read_sql_query("SELECT * FROM friends", con)
# oOwnedGames = pd.read_sql_query("SELECT * FROM ownedgames", con)
con.close()

# 6. Anzahl Freunde -> freundeskonnektivität
#  * s screenshot
#   * eventuell die Anzahl der Freunde mit einbringen

# ablauf
# 1. wähle sample von Spielern
# für jeden spieler
# 2. bestimme freunde von Spieler als set, anzahl der freunde
# 3. filtere freunde, die nicht als players eingetragen sind heraus
# 4. bestimme freunde von freunden
# 5. intersecte mit freunden des unt. spielers
# 6. mean des der fruendesverhältnisse


def get_Player(lPlayerId):
    return oPlayers[oPlayers["Id"] == lPlayerId]


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


def explore_list_of_players(aPlayersToExplore):
    dicFriendsGameConnectivity = {"playerId": [],
                                  "meanFriendsConnection": [], "maxFriendsConnection": [], "numberOfFriends": []}

    # für jeden spieler
    # 2. bestimme freunde von Spieler als set, anzahl der freunde
    # 3. filtere freunde, die nicht als players eingetragen sind heraus
    # 4. bestimme freunde von freunden
    # 5. intersecte mit freunden des unt. spielers
    # 6. mean des der fruendesverhältnisse

    for lExploredPlayerId in aPlayersToExplore:
        # lExploredPlayerId = 76561198063135040
        aPlayerFriends = get_player_friends_crawled(lExploredPlayerId)
        lNumberOfFriends = len(aPlayerFriends)
        # handle if no friends are in db
        # or there is only the relation to the parentplayer
        if lNumberOfFriends == 0 or lNumberOfFriends == 1:
            continue
        # generate a set to allow intersections
        sePlayerFriends = set(aPlayerFriends)

        aFriendsConnections = []
        for lFriendPlayerId in aPlayerFriends:
            seFriendPlayerFriends = set(get_player_friends(lFriendPlayerId))
            # get set of common friends divide it by the number of friends
            dFriendConnection = (len(
                sePlayerFriends & seFriendPlayerFriends)) / lNumberOfFriends
            # print("E: %i, F: %i (%i) (co: %i): %f" % (lExploredPlayerId, lFriendPlayerId, len(
            # seFriendPlayerFriends) - 1, len(sePlayerFriends &
            # seFriendPlayerFriends),  dFriendConnection))
            aFriendsConnections.append(dFriendConnection)

        dMeanFriendsConnection = np.mean(aFriendsConnections)
        dMaxFriendsConnection = np.max(aFriendsConnections)
        # add data to dataframe
        dicFriendsGameConnectivity["playerId"].append(lExploredPlayerId)
        dicFriendsGameConnectivity["meanFriendsConnection"].append(
            dMeanFriendsConnection)
        dicFriendsGameConnectivity["maxFriendsConnection"].append(
            dMaxFriendsConnection)
        dicFriendsGameConnectivity["numberOfFriends"].append(lNumberOfFriends)

        print("player %i, friendsConnection: %f, maxFriendsConnection: %f  nOfFriends: %i" %
              (lExploredPlayerId, dMeanFriendsConnection, dMaxFriendsConnection, lNumberOfFriends))
    return dicFriendsGameConnectivity


# ----- main program ---------


dicFriendsGameConnectivity = {"playerId": [],
                              "meanFriendsConnection": [], "maxFriendsConnection": [], "numberOfFriends": []}
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
    dicFriendsGameConnectivity["meanFriendsConnection"].extend(
        dicResult["meanFriendsConnection"])
    dicFriendsGameConnectivity["maxFriendsConnection"].extend(
        dicResult["maxFriendsConnection"])
    dicFriendsGameConnectivity["numberOfFriends"].extend(
        dicResult["numberOfFriends"])

oExportDataFrame = pd.DataFrame(dicFriendsGameConnectivity)
# append data if file already existend
if bFileExistend:
    oExportDataFrame.to_csv(sOutputFileName, mode='a', header=False)
else:
    oExportDataFrame.to_csv(sOutputFileName)


# ----------------------------------------------------------------------
