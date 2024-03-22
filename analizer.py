import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

name = "numpy"

file = open('numpy.csv')

times = []
avs = []
maxs = []
totals = []
ratios = []

for line in file:
    if line[0] == 't':
        continue
    sections = line.split(',')
    times.append(float(sections[0]))
    avs.append(float(sections[3]))
    maxs.append(float(sections[4]))
    totals.append(float(sections[5].strip()))
    ratios.append(float(sections[6].strip()))

times = np.array(times)
avs = np.array(avs)
maxs = np.array(maxs)
totals = np.array(totals)
ratios = np.array(ratios)

times = times / 3.6e+6

print(spearmanr(times, avs))
print(spearmanr(times, maxs))
print(spearmanr(times, totals))
print(spearmanr(times, ratios))


def plot(values, vname):
    plt.title(f'{vname} vs Time For {name}')

    plt.ylabel("Time (hours)")
    plt.xlabel(vname)
    plt.scatter(values, times)
    plt.show()


plot(avs, 'average cyclomatic complexity')

plot(maxs, 'max cyclomatic complexity')

plot(totals, 'total cyclomatic complexity')

plot(ratios, 'total cyclomatic complexity over lines of code.')
