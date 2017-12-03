import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt


# read csv
oData = pd.read_csv("friendsgames.csv")
print(oData[["numberOfFriends", "numberOfGames", "commonGames"]].describe())

# set figure size
plt.figure(num=None, figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')

# dependend from number of friends
oPlot = sb.jointplot(x="commonGames", y="numberOfFriends", data=oData)
oPlot.set_axis_labels("games in common with friends", "number of friends")
oPlot.fig.savefig("friendsgames_1.png")
plt.clf()

oPlot = sb.jointplot(x="commonGames", y="numberOfFriends",
                     data=oData, kind="kde")
oPlot.set_axis_labels("games in common with friends", "number of friends")
oPlot.fig.savefig("friendsgames_2.png")
plt.clf()

# dependend from number of games owned
oPlot = sb.jointplot(x="commonGames", y="numberOfGames", data=oData)
oPlot.set_axis_labels("games in common with friends", "number of games")
oPlot.fig.savefig("friendsgames_3.png")
plt.clf()

oPlot = sb.jointplot(x="commonGames", y="numberOfGames",
                     data=oData, kind="kde")
oPlot.set_axis_labels("games in common with friends", "number of games")
oPlot.fig.savefig("friendsgames_4.png")
plt.clf()

# save hist
oPlot = sb.distplot(oData["commonGames"], kde=True, bins=30)
oPlot.set_xlim(0, 1)
oPlot.set_xlabel("games in common with friends")
oPlot.get_figure().savefig("friendsgames_5.png")
plt.clf()
