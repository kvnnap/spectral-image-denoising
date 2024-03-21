# This script is used to get some stats
# for experiment 1 sample results

import sys
import os
import argparse
import itertools
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.run import RunData, RunResult, ParameterSpace
from utils.versioning import get_version
from utils.serialisation import save, load
from visualisation.run import ResultViewer
from utils.image import set_base_path

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
    parser.add_argument('--result', default='smb/exp_1b/merged_result_gray_minimize.json', help='The result to load')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    args = parser.parse_args()
    set_base_path(args.image_base)

    resultPath = args.result
    runData = load(resultPath)

    # deduce the span
    # process data to rows/cols
    header = ['id', 'name', 'ref-noisy', 'imageLoader', 'metric', 'score', 'thresholding', 'search', 'iterations', 'iter', 'denoiser', 'denoiser_coeff', 'sample', 'time', 'message']
    filterDict = { key: set() for key in header if not(key in ['id', 'score', 'sample', 'iter', 'time', 'message']) }
    row = []
    scoreIndex = header.index('score')
    iterIndex = header.index('iter')
    timeIndex = header.index('time')
    messageIndex = header.index('message')
    for run in runData.runs:
        dp = run.denoiserParams
        for key in filterDict:
            filterDict[key].update({ dp.get_value(key) })
        rowItem = [dp.get_value(val) for val in header]
        rowItem[scoreIndex] = run.denoiserResult.fun
        rowItem[iterIndex] = len(run.denoiserResult.func_vals)
        rowItem[timeIndex] = round(run.time * 1e-9)
        rowItem[messageIndex] = run.denoiserResult.message if hasattr(run.denoiserResult, 'message') else ''
        row.append(rowItem)
    row.sort(key=lambda r: r[scoreIndex])

    filterDict = {k: sorted(v) for k, v in filterDict.items() if len(v) > 1}

    catToVary = {
        'imageLoader': [ 'gray_tm' ], 
        'ref-noisy': [], 
        'metric': [ 'mse', 'psnr', 'ssim' ]
    }
    filterDict = {k: v if v else filterDict[k] for k,v in catToVary.items()}

    keys = filterDict.keys()
    values = filterDict.values()
    combinations = list(itertools.product(*values))
    filters = [{key: [ value ] for key, value in zip(keys, combination)} for combination in combinations]

    # Grab first row in each
    filtered = [filter_data(header, row, f)[0] for f in filters]

    # runs are sorted by id
    runData.runs.sort(key=lambda r: r.denoiserParams.id)
    runData.runs = [runData.runs[fRow[0]] for fRow in filtered]

    # Stats
    totalItems = len(runData.runs)
    stats = [ 'search', 'denoiser_coeff']
    stats = {s: header.index(s) for s in stats}
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