import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load, save
from utils.array import *
from evaluation.run import Run

def main():
    versionString = get_version().to_string()
    print(versionString)
    parser = argparse.ArgumentParser(description=f'Checks the integrity of a result json file.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='The result file to load')
    parser.add_argument('--output-result', default='output-result.json', help='The result file to save')
    args = parser.parse_args()

    resultPath = args.result
    outputResultPath = args.output_result

    print(f'Loading \'{resultPath}\'')

    runData = load(resultPath)
    validRuns = list(filter(lambda run: not (any(is_not_finite(run.denoiserResult.__dict__[x]) for x in ['x', 'x_iters', 'fun', 'func_vals']) or not hasattr(run, 'bestMetricResults') or run.bestMetricResults is None or is_not_finite(list(run.bestMetricResults.values()))), runData.runs))
    print(f'Removed {len(runData.runs) - len(validRuns)} invalid runs')
    runData.runs = validRuns
    print(f'Saving to {outputResultPath}')
    save(outputResultPath, runData)


# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()
