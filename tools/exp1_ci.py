# This script is used to get the confidence interval / standard deviation of the mean
# for experiment 1 sample results

import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load
import itertools
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def filter_data(header, rowData, filters):
    def condition(row):
        AndResult = True
        for name, listValues in filters.items():
            if not listValues:
                continue
            rowIndex = header.index(name)
            OrResult = False
            for value in listValues:
                OrResult |= row[rowIndex] == value
                if OrResult:
                    break
            AndResult &= OrResult
            if AndResult == False:
                break
        return AndResult
    return list(filter(condition, rowData))

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Finds the standard error of the mean.\n{versionString}')
    parser.add_argument('--result', default='smb/exp_1a/stat_test_result.json', help='Multiple results to load. Add more json with seperate --result flags')
    args = parser.parse_args()

    resultPath = args.result
    runData = load(resultPath)

    # deduce the span
    # process data to rows/cols
    header = ['id', 'name', 'ref-noisy', 'imageLoader', 'metric', 'score', 'thresholding', 'search', 'iterations', 'denoiser', 'denoiser_coeff', 'sample']
    filterDict = { key: set() for key in header if not(key in ['id', 'score', 'sample', 'denoiser']) }
    row = []
    scoreIndex = header.index('score')
    for run in runData.runs:
        dp = run.denoiserParams
        for key in filterDict:
            filterDict[key].update({ dp.get_value(key) })
        rowItem = [dp.get_value(val) for val in header]
        rowItem[scoreIndex] = run.denoiserResult.fun
        row.append(rowItem)
    filterDict = {k: v for k, v in filterDict.items() if len(v) > 1}

    keys = filterDict.keys()
    values = filterDict.values()
    combinations = list(itertools.product(*values))
    filters = [{key: [ value ] for key, value in zip(keys, combination)} for combination in combinations]
    filtered = [filter_data(header, row, f) for f in filters]

    # this can change
    filtered = [[p[scoreIndex] for p in x] for x in filtered]
    #filtered = [{**a, **b} for a, b in zip(filters, [{'scores': x} for x in filtered])]
    filtered = [(a, b) for a, b in zip(filters, filtered)]

    # indexed = {key: value  for key, value in zip(filters, f)}

    # Sort by the mean for easier understanding of the data
    filtered = sorted(filtered, key=lambda f: np.mean(f[1]))

    toPlot = []
    for i, (metaData, scores) in enumerate(filtered):
        n = len(scores)
        mean = np.mean(scores)
        sampleStd = np.std(scores, ddof=1)
        stdDeviationOfMean = sampleStd / np.sqrt(n)
        # within 2 std deviations i.e. 95%
        z = 2.0
        #z = norm.ppf(1 - (1 - 0.95))
        step = z * stdDeviationOfMean
        confidenceInterval = (mean - step, mean + step)
        print(f'{i}) {metaData} Interval: {confidenceInterval} Distance: {step * 2.0}')
        toPlot.append((i, mean, step))

    # Sample confidence intervals
    #intervals = [(2, 0.5), (3, 0.8), (1, 0.3)]
    intervals = toPlot

    # Extract data from intervals
    labels, midpoints, errors = zip(*intervals)

    # Plotting
    plt.errorbar(midpoints, range(len(midpoints)), xerr=errors, fmt='o', capsize=5)
    for i, (midpoint, error) in enumerate(zip(midpoints, errors)):
        plt.fill_betweenx([0, i], midpoint - error, midpoint + error, alpha=0.3)
    plt.yticks(range(len(labels)), labels)  # Setting yticks for indexing
    plt.ylabel('Data Points')
    plt.xlabel('Midpoints')
    plt.title('Confidence Intervals')
    plt.show()

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()