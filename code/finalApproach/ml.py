idofmaxplayer = 0
maxfriends = 0
oldestAcc = time.time()
newestAcc = 0
maxGameTime = 0
maxGameNumber = 0
earliestLogOff = time.time()
lastLogOff = 0

friendNumberList = list()
oldestAccList = list()
maxGameTimeList = list()
maxGameNumberList = list()
logOffList = list()

for playerTuple in playerTupleList:
    friendNumberList.append(len(playerTuple.friends))
    oldestAccList.append(playerTuple.mainPlayer.TimeCreated)
    maxGameTimeList.append(dataAnalysis.calcCompleteGameTime(playerTuple.mainPlayer))
    maxGameNumberList.append(len(playerTuple.mainPlayer.OwnedGames))
    logOffList.append(playerTuple.mainPlayer.LastLogOff)
    for friend in playerTuple.friends:
        oldestAccList.append(friend.TimeCreated)
        maxGameTimeList.append(dataAnalysis.calcCompleteGameTime(friend))
        maxGameNumberList.append(len(friend.OwnedGames))
        logOffList.append(friend.LastLogOff)

friendNumberList = sorted(friendNumberList)
oldestAccList = sorted(oldestAccList)
maxGameTimeList = sorted(maxGameTimeList)
maxGameNumberList = sorted(maxGameNumberList)
logOffList = sorted(logOffList)

lowerFriend, maxfriends = dataAnalysis.getListLimits(friendNumberList)
oldestAcc, newestAcc = dataAnalysis.getListLimits(oldestAccList)
lowerTime, maxGameTime = dataAnalysis.getListLimits(maxGameTimeList)
lowerGames, maxGameNumber = dataAnalysis.getListLimits(maxGameNumberList)
earliestLogOff, lastLogOff = dataAnalysis.getListLimits(logOffList)

now = time.time()
maxAge = now - oldestAcc
maxLogOffValue = lastLogOff -earliestLogOff

xComplete = list()
yComplete = list()

zeroTargets = 0

for playerTuple in playerTupleList:
    friendsNormalized = len(playerTuple.friends) / maxfriends
    if friendsNormalized > 1:
        friendsNormalized = 1
    averageFriendAge = 0
    averageFriendPlayTime = 0
    averageFriendGames = 0
    averageLogOffTime = 0
    for friend in playerTuple.friends:
        friendAge = (now - friend.TimeCreated) / maxAge
        if friendAge > 1:
            friendAge = 1
        averageFriendAge += friendAge
        friendPlayTime = dataAnalysis.calcCompleteGameTime(friend) / maxGameTime
        if friendPlayTime > 1:
            friendPlayTime = 1
        averageFriendPlayTime += friendPlayTime
        friendGames = len(friend.OwnedGames) / maxGameNumber
        if friendGames > 1:
            friendGames = 1
        averageFriendGames+= friendGames
        friendLogOffTime = friend.LastLogOff
        if friendLogOffTime > lastLogOff:
            friendLogOffTime = lastLogOff
        if friendLogOffTime < earliestLogOff:
            friendLogOffTime = earliestLogOff + 1
        friendLogOffTime = (friendLogOffTime - earliestLogOff) / maxLogOffValue
        if math.isnan(friendLogOffTime):
            friendLogOffTime = 1 / maxLogOffValue
        averageLogOffTime += friendLogOffTime

    averageFriendAge /= len(playerTuple.friends)
    averageFriendPlayTime /= len(playerTuple.friends)
    averageFriendGames /= len(playerTuple.friends)
    averageLogOffTime /= len(playerTuple.friends)
    xComplete.append([friendsNormalized, averageFriendAge, averageFriendPlayTime, averageFriendGames])
    target = dataAnalysis.classifyPlayer(playerTuple.mainPlayer)
    if target == 0:
        zeroTargets+=1
    yComplete.append([target])

zeroTargets = zeroTargets / len(playerTupleList)
#print("percent zero targets:" + str(zeroTargets))

x = xComplete[0:9000]
y = yComplete[0:9000]

xTest = xComplete[9000:9999]
yTest = yComplete[9000:9999]

print("start training")
trainigTime = time.time()

clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(10,10,10), random_state=1)
model = clf.fit(x, np.array(y).ravel())
result = model.score(xTest, np.array(yTest).ravel())
print(result)
