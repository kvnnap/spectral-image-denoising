# This script is used to get some stats
# for experiment 1 sample results

from pathlib import Path
import sys
import os
import argparse
import itertools

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load, save, save_text
from utils.string import comma_to_list, get_prefix, tables_to_csv, tables_to_latex
from utils.constants import NAMEMAP, CONV

from visualisation.row_data import RowData

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Finds the top scorers.\n{versionString}')
    # offline/smb/exp_1b/result_gray_all_merged.json
    parser.add_argument('--result', default='offline/smb/exp_1b/result_gray_all_merged.json', help='The result to load')
    parser.add_argument('--image-loaders', default='gray_aces_tm_nogamma', help='Which image loaders will be considered (comma separated) (tabbed)')
    parser.add_argument('--metrics', default='', help='Metrics (comma separated) (tabbed)')
    parser.add_argument('--use-best-metrics', default=False, action='store_true', help='Sort by best metrics. There will be no filtering occuring using one metric')
    parser.add_argument('--out-table', default='offline/smb/exp_1c/config_top_runs_gray_aces_tm_ng.csv', help='The config produced for running the samples')
    args = parser.parse_args()

    print(f'Loading {args.result} and saving top to {args.out_table}')
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
    rDict = {r.denoiserParams.id: r for r in runData.runs}
    runData.runs = [rDict[fRow[0]] for fRow in filtered]
    
    tables = []
    # Generate summary table
    table = []
    header = ['scene', *filterDict['metric']]
    table.append(header)
    sceneIndex = RowData.HEADER.index('ref-noisy')
    metricIndex = RowData.HEADER.index('metric')
    for scene in filterDict['ref-noisy']:
        #sRuns = [r for r in runData.runs if r.denoiserParams.]
        sceneName = get_prefix(scene.split('-')[0], -2)
        mappedName = NAMEMAP[sceneName]

        sceneRowData = [r for r in filtered if r[sceneIndex] == scene]
        data = []
        for metric in filterDict['metric']:
            row = [r for r in sceneRowData if r[metricIndex] == metric]
            data.append(CONV[metric](row[0][scoreIndex]))
        table.append([mappedName, *data])
    tables.append(table)

    # Generate detailed tables
    denIndex = RowData.HEADER.index('denoiser_coeff')
    thresIndex = RowData.HEADER.index('thresholding')
    header = ['scene', 'metric', 'score', 'denoiser', 'threshold']
    table = [ header ]
    for scene in filterDict['ref-noisy']:
        #sRuns = [r for r in runData.runs if r.denoiserParams.]
        sceneName = get_prefix(scene.split('-')[0], -2)
        mappedName = NAMEMAP[sceneName]
        sceneRowData = [r for r in filtered if r[sceneIndex] == scene]

        # table = [ header ]
        for row in sceneRowData:
            data = [ mappedName ]
            for index in [metricIndex, scoreIndex, denIndex, thresIndex]:
                if index == scoreIndex:
                    metric = row[metricIndex]
                    data.append(CONV[metric](row[scoreIndex]))
                else:
                    data.append(row[index])
            table.append(data)

    tables.append(table)

    # CSV
    path = args.out_table
    csvStr = tables_to_csv(tables)
    csvPath = str(Path(path).with_suffix('.csv'))
    save_text(csvPath, csvStr)

    # LaTeX
    latexStr = tables_to_latex(tables)
    latexPath = str(Path(path).with_suffix('.tex'))
    save_text(latexPath, latexStr)



# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()