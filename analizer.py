import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

name = "test"

file = open('text.csv')

times = []
avs = []
maxs = []
totals = []

for line in file:
    if line[0] == 't':
        continue
    sections = line.split(',')
    times.append(float(sections[0]))
    avs.append(float(sections[3]))
    maxs.append(float(sections[4]))
    totals.append(float(sections[5].strip()))

times = np.array(times)
avs = np.array(avs)
maxs = np.array(maxs)
totals = np.array(totals)

times = times / 3.6e+6

print(spearmanr(times, avs))
print(spearmanr(times, maxs))
print(spearmanr(times, totals))

ranks = np.arange(1, len(avs) + 1)
correlation_curve = [spearmanr(avs[:i], times[:i])[0] for i in ranks]

# Plot Spearman correlation curve
plt.plot(ranks, correlation_curve, marker='o')

plt.title(f'Average Cyclomatic Complexity vs Time For {name}')

plt.ylabel("Time (hours)")
plt.xlabel("Average Cyclomatic Complexity")
plt.scatter(avs, times)
plt.show()
# plt.scatter(times, maxs)
# plt.scatter(times, totals)
# plt.show()
