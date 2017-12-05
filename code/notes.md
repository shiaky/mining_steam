### API Results

{PlayerId : Player}

Player:
  Id
  SteamName
  LastLogOff (Unixtime)
  RealName
  PrimaryClanId
  TimeCreated (Unixtime)
  Country
  State
  City
  PrivacyState  (ob profil privat ist oder nicht)
  Banned (war der player schonmal gebannt)
  DaysSinceLastBan
  Friends (liste von SteamIds)
  OwnedGames (Liste von OwnedGame)

OwnedGame:
  GameId
  Playtime
  Playtime 2 Weeks
  Achievements (Dictionary von { Achievement : Erhaltungszeitpunkt (Unixtime) })

{GameId : Game}

Game:
  GameId
  Name
  HasAchievements
  Achievements (Dictionary von {Achievement : Seltenheit des Achievements in Prozent})
  IsFree
  Genres (Liste)
  
  
  
### all seldem achievements
  SELECT g.Id, g.Name, g.HasAchivements, g.IsFree, ga.Curiosity FROM games_achievements as ga INNER JOIN games as g ON g.Id = ga.game_Id WHERE ga.Curiosity > 100;
  
### get all games that are owned by more that 50000 players
SELECT og.game_Id FROM ownedgames as og GROUP BY og.game_Id HAVING COUNT(og.player_Id) > 50000;

### snoop
SELECT og.game_Id, COUNT(og.Id) as owned FROM ownedgames as og GROUP BY og.game_Id ORDER BY COUNT(og.Id) DESC LIMIT 5000;



# snoop

1. freundekonnektivität -> % der Spiele des unters. Spielers die mindestens einer seiner Freunde besitzt
 * nur 1500 häufigsten?
 * zahl zwischen 0 und 1
 * schaue alle spiele an die er besitzt
 * alle spiel die die freunde besitzen
 * 1 ist alle spiele des untersuchten spielers
 * alle rausfiltern, die nicht in der db als player sind

5. Distanz Genre-Distribution des unters. Spielers zu den Genre-dist. der Freunde -> Freundes-Konnektivität
 * genre distribution (vektor der Genres anhand der spielzeit des Spiels), auf 1 normalisiert
 * vektordistanz im raum

6. Anzahl Freunde -> freundeskonnektivität
 * s screenshot
  * eventuell die Anzahl der Freunde mit einbringen





  ## clean db 

  ```
DELETE FROM ownedgames WHERE game_Id IN (SELECt Id FROM games WHERE Name is NULL);
DELETE FROM games WHERE Name is NULL;
DELETE FROM games WHERE Id not in (SELECT  game_Id FROM ownedgames GROUP BY game_Id ORDER BY count(*) DESC LIMIT 1500);
DELETE FROM ownedgames WHERE game_Id not in (Select Id from games);
DELETE FROM friends where player_Id1 not in (SELECT DISTINCT player_Id FROM ownedgames) or player_Id2 not in (SELECT DISTINCT player_Id FROM ownedgames);
DELETE FROM players WHERE Id not in (Select distinct player_Id from ownedgames);
DELETE from games_genres where game_Id not in (Select Id from games); -- run this on the achievements dataset again
VACUUM;
  ```
`SELECT Id FROM players where Id not in (SELECT DISTINCT player_Id FROM ownedgames);`
TODO: delete all nullname players


`SELECT  og.game_Id, count(og.player_Id) FROM ownedgames as og GROUP BY og.game_Id ORDER BY Count(og.player_Id) LIMIT 15;`