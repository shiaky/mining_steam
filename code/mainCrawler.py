#!/usr/bin/env python
from SteamCrawler import Player, Game, SteamCrawler
import datetime

apiKey = ""
crawler = SteamCrawler(apiKey)
playersToCrawl = 2  # takes around 2 hours with crawlingPlayerAchievements enabled
# one api call per game a player owns -> ~ 5-100 api calls per player
crawlPlayerAchievements = True
players, games = crawler.CrawlSteam(playersToCrawl, crawlPlayerAchievements)

print(players)

print(games)
