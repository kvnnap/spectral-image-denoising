# This script is used to get some stats
# for experiment 1 sample results

from pathlib import Path
import sys
import os
import argparse
import itertools

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load, save_text
from utils.string import comma_to_list, tables_to_csv, tables_to_latex, get_mapped_scene_name
from utils.constants import METRICS, CONV

from visualisation.row_data import RowData

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Finds the top scorers.\n{versionString}')
    # offline/smb/exp_1b/result_gray_all_merged.json
    parser.add_argument('--result', default='offline/smb/exp_1b/result_gray_all_merged.json', help='The result to load')
    parser.add_argument('--image-loaders', default='gray_aces_tm_nogamma', help='Which image loaders will be considered (comma separated) (tabbed)')
    parser.add_argument('--metrics', default='', help='Metrics (comma separated) (tabbed)')
    parser.add_argument('--use-best-metrics', action='store_true', help='Sort by best metrics. There will be no filtering occuring using one metric')
    parser.add_argument('--out-table', default='offline/smb/exp_1c/config_top_runs_gray_aces_tm_ng_bm.csv', help='The config produced for running the samples')
    args = parser.parse_args()

    print(f'Loading {args.result} and saving top to {args.out_table}')
    runData = load(args.result)

    catToVary = {
        'imageLoader': comma_to_list(args.image_loaders), 
        'ref-noisy': []
    }

    scoreIndex = RowData.HEADER.index('score')
    searchIndex = RowData.HEADER.index('search')
    sceneIndex = RowData.HEADER.index('ref-noisy')
    metricIndex = RowData.HEADER.index('metric')
    denIndex = RowData.HEADER.index('denoiser_coeff')
    thresIndex = RowData.HEADER.index('thresholding')
    timeIndex = RowData.HEADER.index('time')

    rowData = RowData(runData)
    if args.use_best_metrics:
        rowData.sort_row_data_metric()
    else:
        catToVary['metric'] = comma_to_list(args.metrics)
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
    
    # rowData = RowData(runData)
    # filterDict = rowData.get_filter_dict()

    tables = []
    
    # Generate summary table
    table = []
    if args.use_best_metrics:
        header = ['scene', *METRICS]
        table.append(header)

        for scene in filterDict['ref-noisy']:
            mappedName = get_mapped_scene_name(scene)

            # get actual run
            sceneRowDatum = [r for r in filtered if r[sceneIndex] == scene][0]
            run = rDict[sceneRowDatum[0]]

            data = []
            for metric in METRICS:
                score = run.bestMetricResults[metric][1]
                data.append(CONV[metric](score))
            table.append([mappedName, *data])
    else:
        header = ['scene', *filterDict['metric']]
        table.append(header)
        
        for scene in filterDict['ref-noisy']:
            #sRuns = [r for r in runData.runs if r.denoiserParams.]
            mappedName = get_mapped_scene_name(scene)

            sceneRowData = [r for r in filtered if r[sceneIndex] == scene]
            data = []
            for metric in filterDict['metric']:
                row = [r for r in sceneRowData if r[metricIndex] == metric]
                data.append(CONV[metric](row[0][scoreIndex]))
            table.append([mappedName, *data])

    tables.append(table)

    # Generate detailed tables
    
    # Alter below two arrays to get other columns in data
    header = ['scene', 'metric', 'search', 'denoiser', 'threshold', 'time', 'score']
    dataIndices = [metricIndex, searchIndex, denIndex, thresIndex, timeIndex, scoreIndex]

    table = [ header ]
    for scene in filterDict['ref-noisy']:
        #sRuns = [r for r in runData.runs if r.denoiserParams.]
        mappedName = get_mapped_scene_name(scene)
        sceneRowData = [r for r in filtered if r[sceneIndex] == scene]

        # table = [ header ]
        for row in sceneRowData:
            data = [ mappedName ]
            for index in dataIndices:
                if index == scoreIndex:
                    metric = row[metricIndex]
                    data.append(CONV[metric](row[scoreIndex]))
                else:
                    data.append(str(row[index]))
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