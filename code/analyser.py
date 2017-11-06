#!/usr/bin/env python3

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3

conn = sqlite3.connect("data_05-11-17__5000.db")
players = pd.read_sql_query("SELECT * FROM players;", conn)
# ownedgames_achievements = pd.read_sql_query(
#    "SELECT * FROM ownedgames_achievements;", conn)
ownedgames = pd.read_sql_query("SELECT * FROM ownedgames;", conn)
#genres = pd.read_sql_query("SELECT * FROM genres;", conn)
#games_genres = pd.read_sql_query("SELECT * FROM games_genres;", conn)
# games_achievements = pd.read_sql_query(
#    "SELECT * FROM games_achievements;", conn)
games = pd.read_sql_query("SELECT * FROM games;", conn)
friends = pd.read_sql_query("SELECT * FROM friends;", conn)


# player_games
player_games = players.merge(ownedgames, how="left",
                             left_on="Id", right_on="player_Id")


# number of friends
nr_of_friends = players.merge(friends, how="left", left_on="Id", right_on="player_Id1")[
    ["Id", "player_Id2"]].groupby(["Id"]).count().describe()
print("\nnumber of friends:\n %s" % str(nr_of_friends))

# banned players
banned_players = players[["Banned", "Id"]].groupby(["Banned"]).count()
print("\nbanned players:\n %s" % str(banned_players))


# get privacy state of players
privacy_state = players[["PrivacyState", "Id"]
                        ].groupby(["PrivacyState"]).count()
print("\nget privacy state of player:\n %s" % str(privacy_state))

# count games per user
games_per_user = ownedgames[["player_Id", "Id"]].groupby(
    "player_Id").count().sort_values(by="Id", ascending=False).describe()
print("\ncount games per user:\n %s" % str(games_per_user))

# playtime forever
playtime_forever = ownedgames[["PlaytimeForever"]].describe()
print("\nplaytime forever:\n %s" % str(playtime_forever))

# playtime 2 Weeks
playtime_2weeks = ownedgames[["Playtime2Weeks"]].describe()
print("\nplaytime 2 Weeks:\n %s" % str(playtime_2weeks))


# real name
real_name = players[players.RealName.notnull()]["RealName"].count()
print("\nplayers with real name: %i" % real_name)

# train_df[['Pclass', 'Survived']].groupby(['Pclass'], as_index=False).mean().sort_values(by='Survived', ascending=False)

#print (players["SteamName"])
