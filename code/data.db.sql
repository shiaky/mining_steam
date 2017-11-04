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
COMMIT;
