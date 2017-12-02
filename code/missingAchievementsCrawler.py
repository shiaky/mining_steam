#!/usr/bin/env python
from SteamCrawler import Player, Game, SteamCrawler
from SteamDbStore import SteamDbStore
import json


# set config file
with open("config.json", "r") as json_file:
    config = json.load(json_file)

apiKey = config["token"]

crawler = SteamCrawler(apiKey)
db = SteamDbStore("data.db")
aPlayersToHandle = db.get_players_without_achievements()
aGamesToCrawl = db.get_top_x_games(1500)

print("Players to handle: %i" % len(aPlayersToHandle))

for lPlayerId in aPlayersToHandle:
    print("getting achievements of player %i" % lPlayerId)
    # get list of games of get_player
    aGamesOwned = db.get_ownedgames_of_player(lPlayerId)
    dicAchievementsByGame = crawler.CrawlAchievements(lPlayerId, list(
        aGamesOwned.keys()), aGamesToCrawl)
    db.insert_achievements_to_player(dicAchievementsByGame, aGamesOwned)
