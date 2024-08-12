# This script is used to get some stats
# for experiment 1 sample results

import sys
import os
import argparse
import itertools

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.run import ParameterSpace
from utils.versioning import get_version
from utils.serialisation import load, save
from utils.string import comma_to_list
from visualisation.row_data import RowData

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Finds the top scorers.\n{versionString}')
    parser.add_argument('--result', default='smb/exp_1b/result_gray_all_merged.json', help='The result to load')
    parser.add_argument('--image-loaders', default='', help='Which image loaders will be considered (comma separated) (tabbed)')
    parser.add_argument('--metrics', default='', help='Metrics (comma separated) (tabbed)')
    parser.add_argument('--use-best-metrics', default=False, action='store_true', help='Sort by best metrics. There will be no filtering occuring using one metric')
    parser.add_argument('--for-benchmarks', default=False, action='store_true', help='Set samples to 1 and do not random start, useful to perform benchmarks using --cores 1 later')
    parser.add_argument('--out-config', default='smb/exp_1c/config_top_runs.json', help='The config produced for running the samples')
    args = parser.parse_args()

    print(f'Loading {args.result} and saving top to {args.out_config}')
    runData = load(args.result)

    catToVary = {
        'imageLoader': comma_to_list(args.image_loaders), 
        'ref-noisy': []
    }

    rowData = RowData(runData)
    if args.use_best_metrics:
        rowData.sort_row_data_metric()
    else:
        catToVary['metric'] = comma_to_list(args.metrics)
        scoreIndex = RowData.HEADER.index('score')
        rowData.sort_row_data(scoreIndex)
    
    filterDict = rowData.get_filter_dict()
    filterDict = {k: v if v else filterDict[k] for k,v in catToVary.items()}

    keys = filterDict.keys()
    values = filterDict.values()
    combinations = list(itertools.product(*values))
    filters = [{key: [ value ] for key, value in zip(keys, combination)} for combination in combinations]

    # Grab first row in each
    filtered = [rowData.filter_rows(f)[0] for f in filters]

    # runs are sorted by id
    runData.runs.sort(key=lambda r: r.denoiserParams.id)
    runData.runs = [runData.runs[fRow[0]] for fRow in filtered]

    # Stats
    save(f'{args.out_config}_runData.json', runData)

    # Configs
    paramSpaces = []
    for run in runData.runs:
        dp = run.denoiserParams
        ps = ParameterSpace()
        ps.name = dp.name
        ps.images = [ (dp.pairImage[0], [dp.pairImage[1]]) ]
        ps.imageLoaders = [ dp.imageLoader ]
        ps.metrics = [ dp.metric ]
        ps.thresholds = [ dp.thresholding ]
        ps.searchMethods = [ { k: [v] if k != 'name' else v for k, v in dp.search.items() } ]
        ps.iterations = [ dp.iterations ]
        ps.denoisers = [ { k: [v] if k != 'name' else v for k, v in dp.denoiser.items() } ]
        if not args.for_benchmarks:
            ps.searchMethods[0].update({ 'start': [ 'random' ] })
            ps.samples = 100
        paramSpaces.append(ps)
    
    save(args.out_config, paramSpaces, False)

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()