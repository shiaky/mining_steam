#!/usr/bin/env python3

from dbcon import Dbcon


class SteamDbStore:
    def __init__(self, sPathToDB):
        # create file of not existend
        open(sPathToDB, 'a').close()
        # set db handler
        self.db = Dbcon(sPathToDB)
        # create db schema if not existent
        sDbSchema = """
        BEGIN TRANSACTION;
        CREATE TABLE IF NOT EXISTS `players` (
            `Id`	INTEGER NOT NULL UNIQUE,
            `SteamName`	TEXT,
            `LastLogOff`	INTEGER,
            `RealName`	TEXT,
            `PrimaryClanId`	TEXT,
            `TimeCreated`	INTEGER,
            `Country`	TEXT,
            `State`	TEXT,
            `City`	TEXT,
            `PrivacyState`	INTEGER,
            `Banned`	INTEGER,
            `DaysSinceLastBan`	INTEGER
        );
        CREATE TABLE IF NOT EXISTS `ownedgames_achievements` (
            `ownedgame_Id`	INTEGER NOT NULL,
            `Achievement`	INTEGER NOT NULL,
            `Timestamp`	INTEGER NOT NULL,
            FOREIGN KEY(`ownedgame_Id`) REFERENCES `ownedgames`(`Id`) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS `ownedgames` (
            `Id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            `player_Id`	INTEGER NOT NULL,
            `game_Id`	INTEGER NOT NULL,
            `PlaytimeForever`	INTEGER,
            `Playtime2Weeks`	INTEGER,
            FOREIGN KEY(`player_Id`) REFERENCES `players`(`Id`) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS `genres` (
            `Id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            `Name`	INTEGER
        );
        CREATE TABLE IF NOT EXISTS `games_genres` (
            `game_Id`	INTEGER NOT NULL,
            `genre_id`	INTEGER NOT NULL,
            PRIMARY KEY(`game_Id`,`genre_id`),
            FOREIGN KEY(`genre_id`) REFERENCES `genres`(`Id`) ON DELETE CASCADE,
            FOREIGN KEY(`game_Id`) REFERENCES `games`(`Id`) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS `games_achievements` (
            `game_Id`	INTEGER NOT NULL,
            `Achievement`	TEXT,
            `Curiosity`	REAL,
            FOREIGN KEY(`game_Id`) REFERENCES `games`(`Id`) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS `games` (
            `Id`	INTEGER NOT NULL UNIQUE,
            `Name`	TEXT,
            `HasAchivements`	INTEGER,
            `IsFree`	INTEGER
        );
        CREATE TABLE IF NOT EXISTS `friends` (
            `player_Id1`	INTEGER NOT NULL,
            `player_Id2`	INTEGER NOT NULL,
            PRIMARY KEY(`player_Id1`,`player_Id2`)
        );
        COMMIT;"""
        self.db.execute_sql_query_manipulation_script(sDbSchema)

    def insert_games(self, dicGames):
        """inserting game dictionary's created by the crawler to the
           db structure
        """
        for lId, oGame in dicGames.items():
            # test whether game is already in db,
            # skip if this is the case
            if self.db.execute_sql_query_select("SELECT Id FROM games WHERE Id=?;", (lId,)):
                continue

            # add game
            self.db.execute_sql_query_manipulation(
                "INSERT INTO games (Id, Name, HasAchivements, IsFree) VALUES (?, ?, ?, ?);", (lId, oGame.Name, oGame.HasAchievements, oGame.IsFree))

            # add achievements
            aAchievements = []
            for sAchievement, lCuriosity in oGame.Achievements.items():
                aAchievements.append((lId, sAchievement, lCuriosity))
            self.db.execute_sql_query_manipulation_many(
                "INSERT INTO games_achievements (game_Id, Achievement, Curiosity) VALUES (?, ?, ?);", aAchievements)

            # add genres
            if oGame.Genres:
                for sGenre in oGame.Genres:
                    # test whether genre is existend already
                    aGenreId = self.db.execute_sql_query_select(
                        "SELECT Id FROM genres WHERE Name = ?;", (sGenre,))
                    lGenreId = None
                    if aGenreId:
                        lGenreId = aGenreId[0][0]  # list of tuples
                    else:
                        # insert genre and get the auto generated id
                        lGenreId = self.db.execute_sql_query_manipulation(
                            "INSERT INTO genres (Name) VALUES (?);", (sGenre,))
                    self.db.execute_sql_query_manipulation(
                        "INSERT INTO games_genres (game_Id, genre_Id) VALUES (?,?);", (lId, lGenreId))

    def insert_players(self, dicPlayers):
        for lId, oPlayer in dicPlayers.items():
            # test whether player is already in db,
            # skip if this is the case
            if self.db.execute_sql_query_select("SELECT Id FROM players WHERE Id=?;", (lId,)):
                continue

            # add player
            self.db.execute_sql_query_manipulation(
                "INSERT INTO players (Id, SteamName, LastLogOff, RealName, PrimaryClanId, TimeCreated, Country, State, City, PrivacyState, Banned, DaysSinceLastBan) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (lId, oPlayer.SteamName, oPlayer.LastLogOff, oPlayer.RealName, oPlayer.PrimaryClanId, oPlayer.TimeCreated, oPlayer.Country, oPlayer.State, oPlayer.City, oPlayer.PrivacyState, oPlayer.Banned, oPlayer.DaysSinceLastBan))

            # handle friendship
            for lFriendId in oPlayer.Friends:
                # test whether friendship is already in db
                # if yes, skip
                if self.db.execute_sql_query_select("SELECT null FROM friends WHERE (player_Id1 = ? AND player_Id2 = ?) OR (player_Id1 = ? AND player_Id2 = ?);", (lId, lFriendId, lFriendId, lId)):
                    continue
                # add friendship
                self.db.execute_sql_query_manipulation(
                    "INSERT INTO friends (player_Id1, player_Id2) VALUES (?,?);", (lId, lFriendId))

            # handle owned games
            for oOwnedGame in oPlayer.OwnedGames:
                # insert owned game
                lOwnedGameId = self.db.execute_sql_query_manipulation(
                    "INSERT INTO ownedgames (player_Id, game_Id, PlaytimeForever, Playtime2Weeks) VALUES (?,?,?,?);", (lId, oOwnedGame.Id, oOwnedGame.PlaytimeForever, oOwnedGame.Playtime2Weeks))
                # handle owned games achievements
                aAchievements = []
                for sAchievement, lTimestamp in oOwnedGame.Achievements.items():
                    aAchievements.append(
                        (lOwnedGameId, sAchievement, lTimestamp))
                self.db.execute_sql_query_manipulation_many(
                    "INSERT INTO ownedgames_achievements (ownedgame_Id, Achievement, Timestamp) VALUES (?, ?, ?);", aAchievements)

    def get_player_ids(self):
        aPlayers = self.db.execute_sql_query_select("SELECT Id FROM players;")
        return [lPlayerId[0] for lPlayerId in aPlayers]

    def get_game_ids(self):
        aGames = self.db.execute_sql_query_select("SELECT Id FROM games;")
        return [lGameId[0] for lGameId in aGames]
