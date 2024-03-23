import glob
import os
from copy import copy
from random import randint

import numpy
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from scipy import stats

def trimmed(arr, percent=10):
    trim_count = int(len(arr) * percent / 100)
    sorted_arr = arr[arr[:,0].argsort()]
    trimmed_arr = sorted_arr[trim_count:-trim_count]
#    if you want to trim the time too sort by arr[:,1] and trimm it again.
    return trimmed_arr


def get_file_data(file_name, shuffle):
    file = open(file_name)

    times = []
    avs = []
    maxs = []
    totals = []
    ratios = []

    dt = numpy.dtype([('data', float), ('times', float)])

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

    times = times / 3600

    if shuffle:
        np.random.shuffle(times)

    avt = np.array([avs, copy(times)]).transpose()
    avt = trimmed(avt, 10)

    maxst = np.array([maxs, copy(times)]).transpose()
    maxst = trimmed(maxst, 10)

    totalst = np.array([totals, copy(times)]).transpose()
    totalst = trimmed(totalst, 10)

    ratiost = np.array([ratios, copy(times)]).transpose()
    ratiost = trimmed(ratiost, 10)

    return avt, maxst, totalst, ratiost


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
        array = get_file_data(file, shuffle)
        data.append((name, array))

    for i in range(4):
        plt.figure(figsize=(10, 10))
        plt.title(f'{VALUE_NAMES[i]} vs Time')
        plt.ylabel("Time (hours)")
        plt.xlabel(VALUE_NAMES[i])
        for name, array in data:
            values = array[i].transpose()
            # plt.hist2d(values, times, label=name)
            plt.scatter(values[0], values[1], label=name)
        plt.legend(loc="upper right")
        # plt.savefig(f"{base}_file_{i}.png")
        # plt.clf()
        plt.show()

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
    print('done')

inputs = [('numpy.csv', 'numpy'), ('tensorflow.csv', 'tensorflow'),
        ('pytorch.csv', 'pytorch')]
input1 = [('tensorflow.csv', 'tensorflow')]
input2 = [('numpy.csv', 'numpy')]

plot_all(input1)
# lineup(inputs, 4)
