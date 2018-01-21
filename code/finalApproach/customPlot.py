

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


pdPlotData = pd.read_csv("plot_ml_quality_data.csv")

# pdPlotData = pd.DataFrame(columns=['value', 'class', 'algo'])

# pdPlotData = pdPlotData.append(
#     {'value': 0.74, 'class': "precision", 'algo': "ML"}, ignore_index=True)
# pdPlotData = pdPlotData.append(
#     {'value': 0.86, 'class': "recall", 'algo': "ML"}, ignore_index=True)


# hist for nr of friends
reset_plt()
oSeabornPlot = sb.barplot(x="class", y="value", hue="Method", data=pdPlotData)
oSeabornPlot.set(title="Quality measures of ML")
oSeabornPlot.set(xlabel="Quality measures")
#oSeabornPlot.set(ylabel="Nr. of Players")
oSeabornPlot.set(yticks=np.arange(0, 1.01, 0.1))
oSeabornPlot.get_figure().savefig("quality_ml.png")
plt.clf()
