import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load
from utils.array import *
from evaluation.run import Run

def main():
    versionString = get_version().to_string()
    print(versionString)
    parser = argparse.ArgumentParser(description=f'Checks the integrity of a result json file.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='The result file to load')
    args = parser.parse_args()

    resultPath = args.result

    print(f'Running checks on \'{resultPath}\'')

    runData = load(resultPath)

    # Check that config matches with count
    dps = Run.get_denoiser_params(runData.parameterSpace)
    configIds = [p.id for p in dps]
    runIds = [r.denoiserParams.id for r in runData.runs]
    missing_ids = sorted(set(configIds) - set(runIds))
    badRunIds = list(filter(lambda run: run.denoiserParams.__dict__ != dps[run.denoiserParams.id].__dict__, runData.runs))
    emptyFuncVals = list(filter(lambda run: not run.denoiserResult.func_vals, runData.runs))
    badResultMinimum = list(filter(lambda run: run.denoiserResult.func_vals and min(run.denoiserResult.func_vals) < run.denoiserResult.fun, runData.runs))
    funInFuncVals = list(filter(lambda run: run.denoiserResult.x_iters and run.denoiserResult.x not in run.denoiserResult.x_iters, runData.runs))

    print(f'Runs ({len(dps)}) match totalRuns ({runData.totalRuns}): {runData.totalRuns == len(dps)}')
    print(f'Runs ({len(dps)}) match runs ({len(runData.runs)}): {len(runData.runs) == len(dps)}')
    print(f'Runs sorted: {is_sorted_ascending(runIds)}')
    print(f'Run ids unique: {are_items_unique(runIds)}')
    print(f'Denoiser Params not matching correct ids: {len(badRunIds)}')
    print(f'Empty func_vals: {len(emptyFuncVals)}')
    print(f'Minimum is not fun but contained in func_vals: {len(badResultMinimum)}')
    print(f'fun not contained in func_vals: {len(funInFuncVals)}')
    print(f'Missing runs: {len(missing_ids)}')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()
