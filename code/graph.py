
#######################################
### Exports Friends Graph to D3 JSON ##
#######################################


import json
import sqlite3
import pandas as pd
#import networkx as nx
#import seaborn as sns
#import matplotlib.pyplot as plt


sDb = "../data_27-11-17.db"
oDbCon = sqlite3.connect(sDb)

# create datasets
oPlayers = pd.read_sql_query("SELECT Id FROM players", oDbCon)
oFriends = pd.read_sql_query(
    "SELECT player_Id1, player_Id2 FROM friends", oDbCon)
oDbCon.close()


aPlayers = oPlayers["Id"].head(1000).values
aFriends = oFriends.head(10000).values

# # debug
# aPlayers = [9, 4, 1, 6, 4, 3, 2, 6]
# aFriends = [(9, 1), (4, 9), (2, 6)]

# create D3 json
dicPlayers = {}
for i in range(len(aPlayers)):
    dicPlayers[aPlayers[i]] = i

# set list of nodes
nodes_list = [{"name": str(a)} for a in aPlayers]

# set list of links, if the players are existend
links_list = []
for lP1, lP2 in aFriends:
    if lP1 in dicPlayers.keys() and lP2 in dicPlayers.keys():
        dicLink = {"source": dicPlayers[lP1], "target": dicPlayers[lP2]}
        links_list.append(dicLink)

json_prep = {"nodes": nodes_list, "links": links_list}

json_dump = json.dumps(json_prep, indent=1, sort_keys=True)
filename_out = 'net.json'
json_out = open(filename_out, 'w')
json_out.write(json_dump)
json_out.close()


# # create Graph
# oGraph = nx.Graph()
# oGraph.add_nodes_from(aPlayers)
# oGraph.add_edges_from(aFriends)
# nx.draw(oGraph, with_labels=True)
# plt.savefig("graph.png")


# look at the file with a http server like
# python3 -m http.server
