

# Spielstunden/Tag (proportional zu Registrationsdatum) pro Spieler
# Vergleich der klassenverteilung zwischen Aufteilung nach spielstunden, Aufteilung nach „sind Freunde casual/non-casual Player“
#  Evtl Lohnt sich bei ersterem auch nochmal n Diagramm mit „nur spielstunden“, je nach dem ob wir das betonen wollen oder nicht
# ja ne bell kurve nach spielstunden wäre nice

import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt

# set figure size


def reset_plt():
    plt.figure(num=None, figsize=(10, 8), dpi=90, facecolor='k', edgecolor='k')


def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]


pdPlotData = pd.read_csv("plot_data_big.csv")

# calc playtime per day and diff
pdPlotData["playtimePerDayAccountage"] = pdPlotData.apply(lambda row: (
    (row["totalPlaytime"] / 60) / (row["accountAgePersonal"] / 60 / 60 / 24)), axis=1)
pdPlotData["playtimeFriendsPerDayAccountage"] = pdPlotData.apply(lambda row: (
    (row["meanPlaytimeFriends"] / 60) / (row["meanAccountAgeFriendsPersonal"] / 60 / 60 / 24)), axis=1)
pdPlotData["diffPlaytimeDay"] = pdPlotData.apply(
    lambda row: row["playtimePerDayAccountage"] - row["playtimeFriendsPerDayAccountage"], axis=1)
pdPlotData["diffGameOwnedPlayed"] = pdPlotData.apply(
    lambda row: row["nrOfGamesOwned"] - row["nrOfGamesPlayed"], axis=1)
pdPlotData["totalPlaytime_days"] = pdPlotData.totalPlaytime / 60 / 24
pdPlotData["meanPlaytimeFriends_days"] = pdPlotData["meanPlaytimeFriends"] / 60 / 24
pdPlotData["accountAgePersonal_days"] = pdPlotData["accountAgePersonal"] / 60 / 60 / 24
pdPlotData["meanAccountAgeFriendsPersonal_days"] = pdPlotData["meanAccountAgeFriendsPersonal"] / 60 / 60 / 24
pdPlotData["diffGamesOwned"] = pdPlotData.apply(
    lambda row: row["nrOfGamesOwned"] - row["meanNrOfGamesOwnedFriends"], axis=1)
pdPlotData["diffAccountAgePersonal"] = pdPlotData.apply(
    lambda row: row["accountAgePersonal"] - row["meanAccountAgeFriendsPersonal"], axis=1)

# hist for total playtime
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["totalPlaytime"].values / 60 / 24), bins=None, kde=False)
oSeabornPlot.set(
    title="Total playtime of players")
oSeabornPlot.set(xlabel="total playtime (in days)")
#oSeabornPlot.set(ylabel="Nr. of Players")
oSeabornPlot.get_figure().savefig("total_playtime_days_hist.png")
plt.clf()

# hist account age
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["accountAgePersonal_days"].values), bins=None, kde=False)
oSeabornPlot.set(
    title="Account age of players")
oSeabornPlot.set(xlabel="account age (in days)")
#oSeabornPlot.set(ylabel="Nr. of Players")
oSeabornPlot.get_figure().savefig("account_age_hist.png")
plt.clf()


# plot playtime per day
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["playtimePerDayAccountage"].values), bins=None, kde=False)
oSeabornPlot.set(
    title="Daily playtime of player")
oSeabornPlot.set(xlabel="daily playtime player (in hour/day)")
# oSeabornPlot.set(ylabel="Errorrate")
oSeabornPlot.get_figure().savefig("daily_playtime_hours.png")
plt.clf()


# player playtime per day and friends playtime per day
reset_plt()
oSeabornPlot = sb.jointplot("playtimePerDayAccountage",
                            "playtimeFriendsPerDayAccountage", data=pdPlotData, kind="scatter", size=8)
oSeabornPlot.set_axis_labels(
    "daily playtime player (in hours/day)", "mean daily playtime frieds (in hours/day)")
oSeabornPlot.fig.savefig("joint_dailyplaytime_scatter.png")
plt.clf()

reset_plt()
oSeabornPlot = sb.jointplot("playtimePerDayAccountage",
                            "playtimeFriendsPerDayAccountage", data=pdPlotData, kind="kde", size=8)
oSeabornPlot.set_axis_labels(
    "daily playtime player (in hours/day)", "mean daily playtime frieds (in hours/day)")
oSeabornPlot.fig.savefig("joint_dailyplaytime_kde.png")
plt.clf()

# hist for diff playtime
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["diffPlaytimeDay"].dropna().values), bins=None, kde=False)
oSeabornPlot.set(
    title="Difference of daily playtime player and mean daily playtime of friends")
oSeabornPlot.set(
    xlabel="daily playtime player - mean daily playtime friends (in hours/day)")
oSeabornPlot.get_figure().savefig("diff_playtime.png")
plt.clf()

# hist for diff playtime
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["diffGamesOwned"].dropna().values), bins=None, kde=False)
oSeabornPlot.set(
    title="Difference between number of games owned by player and mean number of games owned by friends")
oSeabornPlot.set(
    xlabel="nr. of games owned player -  mean nr. of games owned friends")
oSeabornPlot.get_figure().savefig("diff_games_owned_player_friends.png")
plt.clf()

# hist for diff accountage
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["diffAccountAgePersonal"].dropna().values / 60 / 60 / 24), bins=None, kde=False)
oSeabornPlot.set(
    title="Difference between account age player and account age friends")
oSeabornPlot.set(
    xlabel="account age player -  mean account age friends (in days)")
oSeabornPlot.get_figure().savefig("diff_accountage_player_friends.png")
plt.clf()

# hist for games owned
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["nrOfGamesOwned"].values), bins=None, kde=False)
oSeabornPlot.set(
    title="Number of games owned")
oSeabornPlot.set(xlabel="number of games owned")
#oSeabornPlot.set(ylabel="Nr. of Players")
oSeabornPlot.get_figure().savefig("games_owned_hist.png")
plt.clf()


# hist for games played
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["nrOfGamesPlayed"].values), bins=None, kde=False)
oSeabornPlot.set(
    title="Number of games played")
oSeabornPlot.set(xlabel="number of games played")
#oSeabornPlot.set(ylabel="Nr. of Players")
oSeabornPlot.get_figure().savefig("games_played_hist.png")
plt.clf()

# hist for diff games owned played
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["diffGameOwnedPlayed"].dropna().values), bins=None, kde=False)
oSeabornPlot.set(
    title="Difference between games owned and games played")
oSeabornPlot.set(
    xlabel="games owned - games played")
oSeabornPlot.get_figure().savefig("diff_owned_played.png")
plt.clf()

# hist for nr of friends
reset_plt()
oSeabornPlot = sb.distplot(
    reject_outliers(pdPlotData["nrOfFriends"].values), bins=None, kde=False)
oSeabornPlot.set(
    title="Number of friends of players")
oSeabornPlot.set(xlabel="number of friends")
#oSeabornPlot.set(ylabel="Nr. of Players")
oSeabornPlot.get_figure().savefig("number_of_friends_hist.png")
plt.clf()


# generate textual statistics

aTargetColumns = [
    ("accountAgePersonal_days", "Age of the player account in days"),
    ("nrOfGamesOwned", "Number of games the player owns"),
    ("nrOfGamesPlayed", "Number of games the player played"),
    ("totalPlaytime_days", "Total playtime of player in days"),
    ("nrOfFriends", "Number of friends the player has"),
    ("meanNrOfGamesOwnedFriends", "Mean number of games owned by friends"),
    ("meanNumberOfPGameslayedFriends", "Mean number of games played by friends"),
    ("meanPlaytimeFriends_days", "Mean playtime of friends"),
    ("meanAccountAgeFriendsPersonal_days",
     "Mean age of the friends accounts in days"),
    ("playtimePerDayAccountage", "Mean playtime of player in hours/day"),
    ("playtimeFriendsPerDayAccountage", "Mean playtime of friends in hours/day"),
    ("diffPlaytimeDay", "Difference playtime player - playtime friends in hours/day"),
    ("diffGameOwnedPlayed", "Difference games owned - games played of player"),
    ("diffGamesOwned", "Difference games owned player friends"),
    ("diffAccountAgePersonal", "Difference account age personal")
]

for sSelector, sTitle in aTargetColumns:
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("### " + sTitle + " ###")
    print(pdPlotData[sSelector].describe())
    print()
