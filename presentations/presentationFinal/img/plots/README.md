## Plots

Alle Plots außer Scatter/KDE sind um Extremwerte bereinigt mit ((wert-mean)< 2*std)

Die Anzahl der Bins in den Hist-Plots wurde in den Hist-Plots mit der Freedman-Diaconis Formel automatisch berechnet.

### total_playtime_days_hist.png
Summierte Gesamtspielzeit der Spieler in Tagen

### account_age_hist.png
Alter der accounts der spieler nach der Formel (lastLogOff - createDate) in Tagen

### daily_playtime_hours.png
Durchschnittliche Spilezeit in Stunden pro Tag der Spieler

### joint_dailyplaytime_scatter.png (nicht in Präsentation)
Durchschnittliche Spielzeit der Spieler mit mittlerer durchschnittlicher Spielzeit der Freunde

### joint_dailyplaytime_kde.png (nicht in Präsentation)
Siehe vorheriger, nur mit KDE bereinigt

## diff_playtime.png
Differenz (dailyPlaytimePlayer - meanDailyPlaytimeFriends) in Stunden
d < 0 => Freunde spielen mehr
d > 0 => Spieler spielt mehr als Freunde

### games_owned_hist.png (muss nicht in Präsi)
Anzahl der Spiele, die ein Spieler besitzt (muss sie nicht gespielt haben)

### games_played_hist.png (muss nicht in Präsi)
Anzahl der Spiele, die ein Spieler mindestens einmal gestartet hat

### diff_owned_played.png (muss nicht in Präsi)
Differenz (gamesOwned - gamesPlayed) ... sagt aus, wie viele Spiele im Durchschnitt nicht gespielt wurden



