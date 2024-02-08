import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import save, load

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Merges run data from multiple files.\n{versionString}')
    parser.add_argument('--result', action='append', help='Multiple results to load. Add more json with seperate --result flags')
    parser.add_argument('--merged-result', default='merged.json', help='File path to merged result')
    args = parser.parse_args()

    resultPath = args.result
    mergedResultPath = args.merged_result
    if not resultPath:
        print('No input')
        return

    runData = load(resultPath[0])
    # Temporary solution, merge results in one view
    # IMPORTANT: NOT ALL INFO FROM BOTH RUNS IS PRESERVED
    # RUN IDS are changed to avoid duplicates in views
    for rPath in resultPath[1:]:
        otherRunData = load(rPath)
        runData.parameterSpace.extend(otherRunData.parameterSpace)
        for otherRunDatum in otherRunData.runs:
            otherRunDatum.denoiserParams.id += runData.totalRuns
            runData.runs.append(otherRunDatum)
        runData.totalRuns += otherRunData.totalRuns

    runData.version = get_version().to_dict()
    runData.cores = -1
    
    save(mergedResultPath, runData)
    save(f'{mergedResultPath}.norefs.json', runData, False)

    print(f'Merged {len(runData.runs)} results')


# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

