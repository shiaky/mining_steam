#!/usr/bin/env python
from SteamCrawler import Player, Game, SteamCrawler
from SteamDbStore import SteamDbStore
import datetime

apiKey = "38306EC9A593F8A835065D5A8F87BC98"
crawler = SteamCrawler(apiKey)
playersToCrawl = 10  # takes around 2 hours with crawlingPlayerAchievements enabled
# one api call per game a player owns -> ~ 5-100 api calls per player
crawlPlayerAchievements = True


##################################################
db = SteamDbStore("data.db")

for lRound in range(100):
    print("Round %i, getting %i players total" %
          (lRound, (lRound + 1) * playersToCrawl))
    players, games = crawler.CrawlSteam(
        playersToCrawl, crawlPlayerAchievements)
    db.insert_games(games)
    db.insert_players(players)
