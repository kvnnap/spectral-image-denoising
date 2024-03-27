# This script is used to get some stats
# for experiment 1 sample results

import sys
import os
import argparse
import itertools
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load
from visualisation.run import ResultViewer
from visualisation.row_data import RowData
from utils.image import set_base_path

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Finds the top scorers.\n{versionString}')
    parser.add_argument('--result', default='smb/exp_1b/merged_result_gray_minimize.json', help='The result to load')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    args = parser.parse_args()
    set_base_path(args.image_base)

    resultPath = args.result
    runData = load(resultPath)

    rowData = RowData(runData)
    scoreIndex = RowData.HEADER.index('score')
    rowData.sort_row_data(scoreIndex)

    catToVary = {
        'imageLoader': [ 'gray_tm' ], 
        'ref-noisy': [], 
        'metric': [ 'mse', 'psnr', 'ssim' ]
    }
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
    totalItems = len(runData.runs)
    stats = [ 'search', 'denoiser_coeff']
    stats = {s: RowData.HEADER.index(s) for s in stats}
    results = {s: { k: [count, totalItems, count / totalItems * 100] for k, count in Counter([r[sId] for r in filtered]).items() } for s, sId in stats.items()}
    print(results)

    # # Configs
    # paramSpaces = []
    # for run in runData.runs:
    #     dp = run.denoiserParams
    #     ps = ParameterSpace()
    #     ps.name = dp.name
    #     ps.images = [ (dp.pairImage[0], [dp.pairImage[1]]) ]
    #     ps.imageLoaders = [ dp.imageLoader ]
    #     ps.metrics = [ dp.metric ]
    #     ps.thresholds = [ dp.thresholding ]
    #     ps.searchMethods = [ { k: [v] if k != 'name' else v for k, v in dp.search.items() } ]
    #     # ps.searchMethods[0].update({ 'start': [ 'random' ] })
    #     ps.iterations = [ dp.iterations ]
    #     ps.denoisers = [ { k: [v] if k != 'name' else v for k, v in dp.denoiser.items() } ]
    #     ps.samples = 100
    #     paramSpaces.append(ps)
    
    # save('config_top_runs.json', paramSpaces, False)
        

    app = ResultViewer(runData)
    app.mainloop()
    



# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()