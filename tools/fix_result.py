import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import save, load

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Fix the result array score.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='Result to fix')
    parser.add_argument('--fixed-result', default='fixed_result.json', help='File path to fixed result')
    args = parser.parse_args()

    resultPath = args.result
    fixedResultPath = args.fixed_result

    runData = load(resultPath)
    runData.version = get_version().to_dict()
    runData.cores = -1
    for run in runData.runs:
        run.denoiserResult.fix()

    save(fixedResultPath, runData)
    print(f'Done')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

