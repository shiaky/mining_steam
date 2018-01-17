#!/usr/bin/env python
from SteamCrawler import Player, Game, SteamCrawler
from SteamDbStore import SteamDbStore
import json
import numpy as np
from multiprocessing.pool import ThreadPool
import sys


# set number of threads
lNumberOfThreads = 4

# set ThreadPool
oPool = ThreadPool(processes=lNumberOfThreads)


# set config file
with open("config.json", "r") as json_file:
    config = json.load(json_file)


# ------- function definition -------


def crawl_players_achievements(apiKey, aPlayersToHandle, aGamesToCrawl):
    crawler = SteamCrawler(apiKey)
    db = SteamDbStore("data.db")
    for lPlayerId in aPlayersToHandle:
        print("getting achievements of player %i" % lPlayerId)
        # get list of games of get_player
        aGamesOwned = db.get_ownedgames_of_player(lPlayerId)
        dicAchievementsByGame = crawler.CrawlAchievements(lPlayerId, list(
            aGamesOwned.keys()), aGamesToCrawl)
        # print(dicAchievementsByGame)
        db.insert_achievements_to_player(dicAchievementsByGame, aGamesOwned)

    return 1


# --- main code ------


apiKey = config["token"]

pThreads = []
db = SteamDbStore("data.db")
aPlayersToHandle = db.get_players_without_achievements()
aPlayersToHandleThreadsplit = np.array_split(
    aPlayersToHandle, lNumberOfThreads)
aGamesToCrawl = db.get_top_x_games(1500)

print("Players to handle: %i" % len(aPlayersToHandle))

# clean data
# del aPlayersToHandle
del db

# ---- debug ------

crawl_players_achievements(apiKey, aPlayersToHandle, aGamesToCrawl)
sys.exit(1)


# ------ END --- debug -----


for i in range(len(aPlayersToHandleThreadsplit)):
    print("starting thread %i" % i)
    pThread = oPool.apply_async(
        crawl_players_achievements, (apiKey, aPlayersToHandleThreadsplit[i], aGamesToCrawl))
    pThreads.append(pThread)


# wait for threads finishing
for i in range(len(aPlayersToHandleThreadsplit)):
    print("waiting for thread %i" % i)
    pThreads[i].get()

print("....FIN .....")
