#!/usr/bin/env python
from SteamCrawler import Player, Game, SteamCrawler
from SteamDbStore import SteamDbStore
import datetime
import json
import sys
import numpy as np

with open("config.json", "r") as json_file:
    config = json.load(json_file)

apiKey = config["token"]
crawler = SteamCrawler(apiKey)
playersToCrawlPerCycle = 2
aArguments = sys.argv
playersToCrawlTotal = int(aArguments[1] if len(aArguments) > 1 else 70)
# one api call per game a player owns -> ~ 5-100 api calls per player
crawlPlayerAchievements = False
# will be overwritten if there are players in db
lStartPlayerId = 76561198063135040


##################################################
sFail = '''

▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
████▌▄▌▄▐▐▌█████
████▌▄▌▄▐▐▌▀████
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

'''

sPirate = '''

    .o oOOOOOOOo                                            OOOo
    Ob.OOOOOOOo  OOOo.      oOOo.                      .adOOOOOOO
    OboO"""""""""""".OOo. .oOOOOOo.    OOOo.oOOOOOo.."""""""""'OO
    OOP.oOOOOOOOOOOO "POOOOOOOOOOOo.   `"OOOOOOOOOP, OOOOOOOOOOOB'
    `O'OOOO'     `OOOOo"OOOOOOOOOOO` .adOOOOOOOOO"oOOO'    `OOOOo
    .OOOO'            `OOOOOOOOOOOOOOOOOOOOOOOOOO'            `OO
    OOOOO                 '"OOOOOOOOOOOOOOOO"`                oOO
   oOOOOOba.                .adOOOOOOOOOOba               .adOOOOo.
  oOOOOOOOOOOOOOba.    .adOOOOOOOOOO@^OOOOOOOba.     .adOOOOOOOOOOOO
 OOOOOOOOOOOOOOOOO.OOOOOOOOOOOOOO"`  '"OOOOOOOOOOOOO.OOOOOOOOOOOOOO
 "OOOO"       "YOoOOOOMOIONODOO"`  .   '"OOROAOPOEOOOoOY"     "OOO"
    Y           'OOOOOOOOOOOOOO: .oOOo. :OOOOOOOOOOO?'         :`
    :            .oO%OOOOOOOOOOo.OOOOOO.oOOOOOOOOOOOO?         .
    .            oOOP"%OOOOOOOOoOOOOOOO?oOOOOO?OOOO"OOo
                 '%\o  OOOO"%OOOO%"%OOOOO"OOOOOO"OOO':
                      `$"  `OOOO' `O"Y ' `OOOO'  o             .
    .                  .     OP"          : o     .
                              :
                              .
'''

##################################################
db = SteamDbStore("data.db")

aCrawledPlayerIds = db.get_player_ids()
aCrawledGameIds = db.get_game_ids()

lNumberOfPlayersCrawled = len(aCrawledPlayerIds)

crawler.SetCrawledPlayers(aCrawledPlayerIds)
crawler.SetCrawledGames(aCrawledGameIds)

# overwrite startplayer if db already has players
if(lNumberOfPlayersCrawled):
    lStartPlayerId = np.random.choice(aCrawledPlayerIds)

print("Steam Crawler v 0.9\n=================")
print("Target count of players: %i\n\n" % playersToCrawlTotal)
print("Current count of players: %i\n\n" % lNumberOfPlayersCrawled)

print(sFail)

while (lNumberOfPlayersCrawled < playersToCrawlTotal):
    print("DB has %i players, trying to get %i players in this round\n Startplayer: %i\n" %
          (lNumberOfPlayersCrawled, playersToCrawlPerCycle, lStartPlayerId))
    players, games = crawler.CrawlSteam(
        playersToCrawlPerCycle, crawlPlayerAchievements, lStartPlayerId)
    db.insert_games(games)
    db.insert_players(players)
    lNumberOfPlayersCrawled += len(players)
    # check wether list of players was not empty
    if len(players) > 0:
        lStartPlayerId = int(list(players.keys())[-1])
    else:
        lStartPlayerId = crawler.GetRandomPlayerId()
        print("No unknown players left... continuing with random player")

print("Target of players reached ... getting last games")
games = crawler.stopCrawling()
db.insert_games(games)

print(sPirate)

print("EXIT.... Bye")
