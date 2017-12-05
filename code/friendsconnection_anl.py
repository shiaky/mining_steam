import pandas as pd
import seaborn as sb
import numpy as np
import matplotlib.pyplot as plt


# read csv
oData = pd.read_csv("friendscon.csv")
print(oData[["meanFriendsConnection",
             "maxFriendsConnection", "numberOfFriends"]].describe())

# set figure size
plt.figure(num=None, figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')

# save hist mean
oPlot = sb.distplot(oData["meanFriendsConnection"], kde=True, bins=30)
oPlot.set_xlim(0, 1)
oPlot.set_xlabel("mean friends connection")
oPlot.get_figure().savefig("friendsconn_1.png")
plt.clf()

# save hist max
oPlot = sb.distplot(oData["maxFriendsConnection"], kde=True, bins=30)
oPlot.set_xlim(0, 1)
oPlot.set_xlabel("maximal friends connection")
oPlot.get_figure().savefig("friendsconn_2.png")
plt.clf()

# dependend from number of friends
oPlot = sb.jointplot(x="meanFriendsConnection",
                     y="numberOfFriends", data=oData)
oPlot.set_axis_labels("mean friends connection", "number of friends")
oPlot.fig.savefig("friendsconn_3.png")
plt.clf()

oPlot = sb.jointplot(x="meanFriendsConnection", y="numberOfFriends",
                     data=oData[np.abs(oData["numberOfFriends"] - np.mean(oData["numberOfFriends"])) <= (3 * np.std(oData["numberOfFriends"]))], kind="kde")
oPlot.set_axis_labels("mean friends connection", "number of friends")
oPlot.fig.savefig("friendsconn_4.png")
plt.clf()
