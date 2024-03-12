import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import save, load

def main():
    versionString = get_version().to_string()
    print(versionString)
    parser = argparse.ArgumentParser(description=f'Sorts results.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='Where to save the sorted JSON Run object')
    args = parser.parse_args()

    resultPath = args.result

    print(f'Sorting runs in \'{resultPath}\'')
    runData = load(resultPath)
    runData.runs = sorted(runData.runs, key=lambda r: r.denoiserParams.id)
    save(resultPath, runData)
    print('Ok, sorted.')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()
