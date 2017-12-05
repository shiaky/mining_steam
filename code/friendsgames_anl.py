import pandas as pd
import seaborn as sb
import numpy as np
import matplotlib.pyplot as plt
import os


# read csv
oData = pd.read_csv("friendsgames.csv")
print(oData[["numberOfFriends", "numberOfGames", "commonGames"]].describe())

# set figure size
plt.figure(num=None, figsize=(10, 6), dpi=80, facecolor='k', edgecolor='k')

# set analyse image directory
sImageDirectory = "analyse_img/"
if not os.path.exists(sImageDirectory):
    os.makedirs(sImageDirectory)

# save hist
oPlot = sb.distplot(oData["commonGames"], kde=True, bins=30)
oPlot.set_xlim(0, 1)
oPlot.set_xlabel("games in common with friends")
oPlot.get_figure().savefig(sImageDirectory + "friendsgames_1.png")
plt.clf()

# dependend from number of friends
oPlot = sb.jointplot(x="commonGames", y="numberOfFriends", data=oData)
oPlot.set_axis_labels("games in common with friends", "number of friends")
oPlot.fig.savefig(sImageDirectory + "friendsgames_2.png")
plt.clf()

oPlot = sb.jointplot(x="commonGames", y="numberOfFriends",
                     data=oData[np.abs(oData["numberOfFriends"] - np.mean(oData["numberOfFriends"])) <= (3 * np.std(oData["numberOfFriends"]))], kind="kde")
oPlot.set_axis_labels("games in common with friends", "number of friends")
oPlot.fig.savefig(sImageDirectory + "friendsgames_3.png")
plt.clf()

# dependend from number of games owned
oPlot = sb.jointplot(x="commonGames", y="numberOfGames", data=oData)
oPlot.set_axis_labels("games in common with friends", "number of games")
oPlot.fig.savefig(sImageDirectory + "friendsgames_4.png")
plt.clf()

oPlot = sb.jointplot(x="commonGames", y="numberOfGames",
                     data=oData[np.abs(oData["numberOfGames"] - np.mean(oData["numberOfGames"])) <= (3 * np.std(oData["numberOfGames"]))], kind="kde")
oPlot.set_axis_labels("games in common with friends", "number of games")
oPlot.fig.savefig(sImageDirectory + "friendsgames_5.png")
plt.clf()
