#!/usr/bin/env python
from SteamCrawler import Player, Game, SteamCrawler
from SteamDbStore import SteamDbStore

crawler = SteamCrawler("")
db = SteamDbStore("data.db")
aMissingGames = db.get_missing_games()
print("Missing Games: %s" % str(aMissingGames))
games = crawler.CrawlSpecificGames(*aMissingGames)
db.insert_games(games)
