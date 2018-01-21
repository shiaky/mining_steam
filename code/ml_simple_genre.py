import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

df = pd.read_csv('feature_genre_4059.csv')

print(df.head())

features = [
    'friendsMainGenre',
    'friendsMainGenrePercentage',
    'numberOfFriendsConsidered',
    'friendsTotalPlaytime',
    'playerTotalPlaytime'
]

label = 'mainGenre'

for col in df:
    if col not in features and col not in [label]:
        del df[col]
    else:
        df[col] = df[col].astype(float)

# Scale total playtime
df[["playerTotalPlaytime"]] = MinMaxScaler().fit_transform(df[["playerTotalPlaytime"]])
df[["friendsTotalPlaytime"]] = MinMaxScaler().fit_transform(df[["friendsTotalPlaytime"]])

df_train, df_test = train_test_split(df, test_size=0.2)
X_train = df_train[list(features)]
y_train = df_train[label]

X_test = df_test[list(features)]
y_test = df_test[label]


def get_info():
    print(df[df['mainGenre'] != 1].count() / df.count())
    print(df[df['playerTotalPlaytime'] < 12000].count() / df.count())


def svm():
    return SVC(kernel='rbf')


def random_forest():
    return RandomForestClassifier(n_estimators=10)


def lr():
    return LinearRegression(normalize=True)


def nb():
    return GaussianNB()


model = random_forest()
y_pred = model.fit(X_train, y_train).predict(X_test)
print("prediction accuracy:", accuracy_score(y_test, y_pred))
print("guessing 1 accuracy:", pd.np.sum(y_test == 1) * 1. / len(y_test))
print("1 count:", pd.np.sum(y_pred == 1) * 1. / len(y_test))
