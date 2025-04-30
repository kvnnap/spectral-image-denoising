import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import save, load

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Filters run data by the reference image starting name.\n{versionString}')
    parser.add_argument('--result', action='append', help='Multiple results to load. Add more json with seperate --result flags')
    parser.add_argument('--filtered-result', default='filtered.json', help='File path to filtered result')
    parser.add_argument('--filter-string', required=True, help='prefix to filter with. runs with this filter are removed')
    parser.add_argument('--fix-ids', default=False, action='store_true', help='Fix ids so they are less than total_runs')

    args = parser.parse_args()

    resultPath = args.result
    filteredResultPath = args.filtered_result

    if not resultPath:
        print('No input')
        return

    runData = load(resultPath[0])
    runData.runs = [r for r in runData.runs if not r.denoiserParams.pairImage[0].startswith(args.filter_string)]

    # sort just in case input was not sorted
    runData.runs.sort(key=lambda r: r.denoiserParams.id)

    # Fix ids ?
    if args.fix_ids:
        id_counter = 0
        for r in runData.runs:
            r.denoiserParams.id = id_counter
            id_counter += 1
        runData.totalRuns = len(runData.runs)

    runData.version = get_version().to_dict()
    runData.cores = -1
    
    save(filteredResultPath, runData)

    print(f'Filtered. New amount is {len(runData.runs)} results')


# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

