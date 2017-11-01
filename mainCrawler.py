from SteamCrawler import Player, Game, SteamCrawler
import datetime

apiKey = "yourApiKeyHere"
crawler = SteamCrawler(apiKey)
playersToCrawl = 1000 # takes around 2 hours with crawlingPlayerAchievements enabled
crawlPlayerAchievements = True  # one api call per game a player owns -> ~ 5-100 api calls per player
players, games = crawler.CrawlSteam(playersToCrawl, crawlPlayerAchievements)

