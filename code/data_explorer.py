import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sqlite3
import json

# Import config
with open("config.json", "r") as json_file:
    config = json.load(json_file)

db = config["db"]
# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(db)
df = pd.read_sql_query("SELECT * FROM players", con)
dfg = pd.read_sql_query("SELECT Id, player_Id, game_Id FROM ownedgames", con)
dff = pd.read_sql_query("SELECT * FROM friends", con)
con.close()

# Convert unix to datetime
df["LastLogOff"] = pd.to_datetime(df["LastLogOff"], unit="s")
df["TimeCreated"] = pd.to_datetime(df["TimeCreated"], unit="s")

# Set total player count
total_count = df["Id"].count()

# Create subframes
dfg_gc = dfg.groupby("player_Id").size().reset_index(name="count")
dff_gc = dff.groupby("player_Id1").size().reset_index(name="count")


def of_total_count(number, precision=2):
    return round(number * 100 / total_count, precision)


# Calculate factors

real_name_factor = of_total_count(df["RealName"].count())
country_factor = of_total_count(df["Country"].count())
city_state_country_factor = of_total_count(
    df[(df.State.notnull() & df.Country.notnull() & df.City.notnull())].count()["City"]
)
ban_factor = of_total_count(df[df["Banned"] == 1].count()["Banned"])
private_factor = of_total_count(df[df["PrivacyState"] != 3]["Id"].count())
active_account_factor = of_total_count(df[df["LastLogOff"].dt.year >= 2017]["Id"].count())
ten_or_more_games_factor = of_total_count(dfg_gc[dfg_gc["count"] >= 10].count()["count"])
fifty_or_more_games_factor = of_total_count(dfg_gc[dfg_gc["count"] >= 50].count()["count"])

print("Currently crawled users: {}".format(total_count))
print("{}% have provided a real name".format(real_name_factor))
print("{}% have set a country".format(country_factor))
print("{}% provided a city and state additionally to the country".format(city_state_country_factor))
print("{}% of the crawled users have set their profile to private".format(private_factor))
print("{}% of the crawled users are active (Logged in at least once this year)".format(active_account_factor))
print("{}% have 10 games or more".format(ten_or_more_games_factor))
print("{}% have 50 games or more".format(fifty_or_more_games_factor))

# Calculate graph data and display graphs

# Game count

# dfg_gc["count"] = pd.cut(dfg_gc["count"], [0, 1, 10, 25, 50, 100, 500, 30000],
#                        labels=["0", "1 - 9", "10 - 24", "25 - 49", "50 - 99", "100 - 499", "500 +"])
# ax = sns.countplot(x=dfg_gc["count"])
# ax.set(xlabel="Game count", ylabel="Number of players")


# Friend count

dff_gc["count"] = pd.cut(dff_gc["count"], [0, 1, 50, 100, 150, 200, 250, 300, 350, 400, 999999],
                         labels=["0", "1 - 49", "50 - 99", "100 - 149", "150 - 199", "200 - 249", "250 - 299",
                                 "300 - 349", "350 - 399", "400+"])

axf = sns.countplot(x=dff_gc["count"])
axf.set(xlabel="Friend count", ylabel="Number of players")
plt.show()
