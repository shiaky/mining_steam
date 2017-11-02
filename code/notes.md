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