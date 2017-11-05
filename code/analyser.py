#!/usr/bin/env python3

import pandas as pd
import sqlite3

conn = sqlite3.connect("data.db")
players = pd.read_sql_query("SELECT * FROM players;", conn)
#TODO: get other tables


#TODO: link tables on ids like:
# movie_db = users.join(ratings.set_index('UserID'), on='UserID')


#print (players["SteamName"])
