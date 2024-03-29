import glob
import os
import statistics
from copy import copy
from random import randint
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


def trimmed(arr, percent=10):
    condition = arr[:, 1] >= 0.00278
    arr = arr[condition]
    print("post invalid= " + str(len(arr)))

    trim_count = int((len(arr) * percent / 100) / 4)
    print("trimmed" + str(trim_count))
    sorted_arr = arr[arr[:, 0].argsort()]
    trimmed_arr = sorted_arr[trim_count:-trim_count]
    #    if you want to trim the time too sort by arr[:,1] and trimm it again.
    sorted_arr = trimmed_arr[trimmed_arr[:, 1].argsort()]
    trimmed_arr = sorted_arr[trim_count:-trim_count]
    return trimmed_arr


def get_file_data(file_name, shuffle=False):
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
    print(file_name)
    print("Average fix time:" + str(statistics.fmean(times)))
    print("Average av complexity:" + str(statistics.fmean(avs)))
    print("Average max complexity:" + str(statistics.fmean(maxs)))
    print("Average total complexity:" + str(statistics.fmean(totals)))
    print("Min time:" + str(min(times)))

    count = 0
    i = 0
    while i < len(times):
        if avs[i] == maxs[i] == totals[i]:
            count += 1
        i += 1
    print(count)
    times = np.array(times)
    avs = np.array(avs)
    maxs = np.array(maxs)
    totals = np.array(totals)
    ratios = np.array(ratios)

    times = times / (24 * 3600)
    print("median times:" + str(statistics.median(times)))
    if shuffle:
        np.random.shuffle(times)

    print("precount" + str(len(avs)))
    avt = np.array([avs, copy(times)]).transpose()
    avt = trimmed(avt, 10)
    print("postcount" + str(len(avt)))

    maxst = np.array([maxs, copy(times)]).transpose()
    maxst = trimmed(maxst, 10)

    totalst = np.array([totals, copy(times)]).transpose()
    totalst = trimmed(totalst, 10)

    ratiost = np.array([ratios, copy(times)]).transpose()
    ratiost = trimmed(ratiost, 10)

    return avt, maxst, totalst, ratiost


VALUE_NAMES = ['Average Cyclomatic Complexity', 'Max Cyclomatic Complexity',
               'Total Cyclomatic Complexity', 'Total Cyclomatic Complexity Over Lines of Code']


def func_all(inputs, func):
    out = {}
    left = []
    for name in VALUE_NAMES:
        left.append(f'{name} statistic')
        left.append(f'{name} p value')

    data = []
    for file, name in inputs:
        values = get_file_data(file, shuffle=False)
        data.append((name, values))
    for i in range(4):
        for name, array in data:
            values = array[i].transpose()
            print(name, VALUE_NAMES[i])
            print(func(values[0], values[1]))
            # if func(values[0], values[1]).pvalue >= 0.95:
            #     return True


def get_stats(inputs):
    func_all(inputs, kendalltau)
    func_all(inputs, spearmanr)


# input = (file, name)
def plot_all(inputs, base='base', shuffle=False):
    data = []
    for file, name in inputs:
        array = get_file_data(file, shuffle)
        data.append((name, array))

    for i in range(4):
        plt.figure(figsize=(15, 10))
        plt.title(f'{VALUE_NAMES[i]} vs Time for {base}')
        plt.ylabel("Time (days)", fontsize=15)
        plt.xlabel(VALUE_NAMES[i], fontsize=15)
        for name, array in data:
            values = array[i].transpose()
            # plt.hist2d(values, times, label=name)
            plt.scatter(values[0], values[1], s=6)
        # plt.legend(loc="upper right")
        plt.savefig(f"{base}_file_{i}.png")
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
input3 = [('pytorch.csv', 'pytorch')]

plot_all(input1, 'TensorFlow')
plot_all(input2, 'NumPy')
plot_all(input3, 'Pytorch')
# lineup(inputs, 4)
