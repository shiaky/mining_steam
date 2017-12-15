# import matplotlib.pyplot as plt
import json
import os.path
# import seaborn as sns
import sqlite3
from multiprocessing.pool import ThreadPool

import numpy as np
import pandas as pd
from sklearn.preprocessing import scale

# Import config
with open("config.json", "r") as json_file:
    config = json.load(json_file)

# --- config------
output_file_name = "playtime.csv"
thread_count = 3
# ----- END -----


db = config["db"]
# check whether file is existend
does_file_exist = os.path.isfile(output_file_name)

# set ThreadPool
thread_pool = ThreadPool(processes=thread_count)

# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(db)
games = pd.read_sql_query("SELECT * FROM games", con)
players = pd.read_sql_query("SELECT * FROM players", con)
friends = pd.read_sql_query("SELECT * FROM friends", con)
owned_games = pd.read_sql_query("SELECT * FROM ownedgames", con)
game_genres = pd.read_sql_query("SELECT * FROM games_genres", con)
con.close()

# Add increment row
games.insert(0, 'inc', range(0, len(games)))

print(games.head())


# Get all games and setup 0-Vector
# Create playtime vector for all friends and player itself
# Throw all together
# Into SciKit
# ???
# Profit

def get_player(player_id):
    return players[players["Id"] == player_id]


def get_playtime_of_game_from_player(player_id, game_id):
    return owned_games[(owned_games["player_Id"] == player_id) & (owned_games["game_Id"] == game_id)][
        "PlaytimeForever"].values[0]


def get_player_friends(player_id):
    tmp_friends = friends[(friends["player_Id1"] == player_id) | (
            friends["player_Id2"] == player_id)]
    return [p1 if p1 != player_id else p2 for p1, p2 in tmp_friends.values]


def get_player_friends_crawled(player_Id):
    """ get the friends existing in the players table only """
    player_friends = get_player_friends(player_Id)

    # filter friends that are not in db
    for lFriendPlayerId in player_friends:
        if lFriendPlayerId not in players["Id"]:
            player_friends.remove(lFriendPlayerId)
    return player_friends


def get_owned_games(player_id):
    return owned_games[owned_games["player_Id"] == player_id]


playtimeVectors = []

for player_id in players["Id"]:
    player_owned_games = get_owned_games(player_id)
    vector = np.zeros(len(games))
    for game_id in games[games["Id"].isin(player_owned_games["game_Id"])]["Id"]:
        playtime = get_playtime_of_game_from_player(player_id, game_id)
        vector[games[games["Id"] == game_id]["inc"]] = playtime
    playtimeVectors.append(
        {"id": player_id, "vector": scale(X=vector, axis=0, with_mean=False, with_std=False, copy=True)})

print(playtimeVectors)
