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
