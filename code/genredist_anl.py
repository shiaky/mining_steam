import pandas as pd
import seaborn as sb
import numpy as np
import matplotlib.pyplot as plt
import os

# read csv
oData = pd.read_csv("genredist.csv")
# filter out nan
oData = oData[oData["meanGenreDistributionDistance"].notnull()]
print(oData[["meanGenreDistributionDistance",
             "numberOfFriends", "numberOfGenres"]].describe())
# TODO: why are there so many nan values ... division by 0?


# set analyse image directory
sImageDirectory = "analyse_img/"
if not os.path.exists(sImageDirectory):
    os.makedirs(sImageDirectory)

# set figure size
plt.figure(num=None, figsize=(10, 6), dpi=80, facecolor='k', edgecolor='k')

# save hist mean
oPlot = sb.distplot(oData["meanGenreDistributionDistance"], kde=True, bins=30)
oPlot.set_xlim(0, 1)
oPlot.set_xlabel("mean genre distribution distance")
oPlot.get_figure().savefig(sImageDirectory + "genredist_1.png")
plt.clf()

# dependend from number of friends
oPlot = sb.jointplot(x="meanGenreDistributionDistance",
                     y="numberOfFriends", data=oData)
oPlot.set_axis_labels("mean genre distribution distance", "number of friends")
oPlot.fig.savefig(sImageDirectory + "genredist_2.png")
plt.clf()

oPlot = sb.jointplot(x="meanGenreDistributionDistance", y="numberOfFriends",
                     data=oData[np.abs(oData["numberOfFriends"] - np.mean(oData["numberOfFriends"])) <= (3 * np.std(oData["numberOfFriends"]))], kind="kde")
oPlot.set_axis_labels("mean genre distribution distance", "number of friends")
oPlot.fig.savefig(sImageDirectory + "genredist_3.png")
plt.clf()


# dependend from number of genres
oPlot = sb.jointplot(x="meanGenreDistributionDistance",
                     y="numberOfGenres", data=oData)
oPlot.set_axis_labels("mean genre distribution distance", "number of genres")
oPlot.fig.savefig(sImageDirectory + "genredist_4.png")
plt.clf()

oPlot = sb.jointplot(x="meanGenreDistributionDistance", y="numberOfGenres",
                     data=oData[np.abs(oData["numberOfGenres"] - np.mean(oData["numberOfGenres"])) <= (3 * np.std(oData["numberOfGenres"]))], kind="kde")
oPlot.set_axis_labels("mean genre distribution distance", "number of genres")
oPlot.fig.savefig(sImageDirectory + "genredist_5.png")
plt.clf()
