# This script is used to get the confidence interval / standard deviation of the mean
# for experiment 1 sample results

import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load, save
from visualisation.row_data import RowData
from evaluation.run import Run

def compute_stats(scores, z = 2.0):
    n = len(scores)
    mean = np.mean(scores)
    sampleStd = np.std(scores, ddof=1)
    stdDeviationOfMean = sampleStd / np.sqrt(n)
    step = z * stdDeviationOfMean
    mean = mean.item()
    step = step.item()
    return {
        'samples': n,
        'mean': mean,
        'step': step,
        'interval': (mean - step, mean + step)
    }

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Finds the standard error of the mean.\n{versionString}')
    parser.add_argument('--result', default='offline/smb/exp_1a/stat_test_result.json', help='Multiple results to load. Add more json with seperate --result flags')
    parser.add_argument('--output', default='offline/smb/exp_1a/stat_test_result_intervals.json', help='Multiple results to load. Add more json with seperate --result flags')
    args = parser.parse_args()

    resultPath = args.result
    runData = load(resultPath)
    rowData = RowData(runData)

    # deduce the span
    # process data to rows/cols
    for p in runData.parameterSpace:
        p.samples = 1
    dps = Run.get_denoiser_params(runData.parameterSpace)
    filters = [{k: [dp.get_value(k)] for k in ['ref-noisy', 'imageLoader', 'metric', 'thresholding', 'search', 'iterations', 'denoiser']} for dp in dps]
    filtered = [rowData.filter_rows(f) for f in filters]

    # this can change
    scoreIndex = RowData.HEADER.index('score')
    filtered = [[p[scoreIndex] for p in x] for x in filtered]
    outResult = [{'denoiserParams': a, 'stats': compute_stats(b)} for a, b in zip(dps, filtered)]

    save(args.output, outResult, False)


# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()