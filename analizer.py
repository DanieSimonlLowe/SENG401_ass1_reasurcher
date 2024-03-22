import glob
import os
from random import randint

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


def get_file_data(file_name, shuffle):
    file = open(file_name)

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

    if shuffle:
        np.random.shuffle(times)

    return avs, maxs, totals, ratios, times


VALUE_NAMES = ['Average Cyclomatic Complexity', 'Max Cyclomatic Complexity',
               'Total Cyclomatic Complexity', 'Total Cyclomatic Complexity Over Lines of Code']


def spear_all(inputs):
    out = {}
    left = []
    for name in VALUE_NAMES:
        left.append(f'{name} statistic')
        left.append(f'{name} p value')

    data = []
    for file, name in inputs:
        avs, maxs, totals, ratios, times = get_file_data(file)
        data.append((name, times, (avs, maxs, totals, ratios)))
    for i in range(4):
        for name, times, array in data:
            values = array[i]
            print(name, VALUE_NAMES[i])
            print(spearmanr(times, values))


# input = (file, name)
def plot_all(inputs, base='base', shuffle=False):
    data = []
    for file, name in inputs:
        avs, maxs, totals, ratios, times = get_file_data(file, shuffle)
        data.append((name, times, (avs, maxs, totals, ratios)))

    for i in range(4):
        plt.figure(figsize=(10, 10))
        plt.title(f'{VALUE_NAMES[i]} vs Time')
        plt.ylabel("Time (hours)")
        plt.xlabel(VALUE_NAMES[i])
        for name, times, array in data:
            values = array[i]
            # plt.hist2d(values, times, label=name)
            plt.scatter(values, times, label=name)
        plt.legend(loc="upper right")
        plt.savefig(f"{base}_file_{i}.png")
        plt.clf()
        # plt.show()


# plot(avs, 'average cyclomatic complexity')
#
# plot(maxs, 'max cyclomatic complexity')
#
# plot(totals, 'total cyclomatic complexity')
#
# plot(ratios, 'total cyclomatic complexity over lines of code.')


def lineup(inputs, count):
    files = glob.glob('lineup/*')
    for f in files:
        os.remove(f)
    for i in range(count):

        num = randint(0, 999999999)
        plot_all(inputs, f'lineup/{num}', shuffle=True)
    num = randint(0, 999999999)
    plot_all(inputs, f'lineup/{num}', shuffle=False)
    f = open("answer.txt", "w")
    f.write(str(num))
    f.close()


lineup([('numpy.csv', 'numpy'), ('tensorflow.csv', 'tensorflow'),
        ('pytorch.csv', 'pytorch')], 4)
