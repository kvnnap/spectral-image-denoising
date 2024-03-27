# This script is used to get some stats
# for experiment 1 sample results

import sys
import os
import argparse
import itertools
import math
import openpyxl
from collections import Counter
from openpyxl.styles import Font

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load, save
from visualisation.row_data import RowData

def compute_stats(rowData, catsConst, catsVar, topPercentage, combsLength=0):
    filterDict = rowData.get_filter_dict()
    masterFilterDict = {k: v if v else filterDict[k] for k,v in catsVar.items()}
    if combsLength <= 0:
        combsLength = len(masterFilterDict)
    # get combinations of filter dict
    combs = itertools.chain.from_iterable(itertools.combinations(masterFilterDict.keys(), r) for r in range(combsLength))
    filterDicts = [{k: masterFilterDict[k] for k in c} for c in combs]

    result = []
    for filterDict in filterDicts:
        filterDict = {**catsConst, **filterDict}
        keys = filterDict.keys()
        values = filterDict.values()
        combinations = list(itertools.product(*values))
        filters = [{key: [ value ] for key, value in zip(keys, combination)} for combination in combinations]

        # Columns to get stats about
        colStatKeys = {s: RowData.HEADER.index(s) for s in masterFilterDict.keys() - filterDict.keys()}

        #filtered = []
        stats=[]
        for f in filters:
            fRows = rowData.filter_rows(f)
            totalRowCount = len(fRows)
            numItems = math.ceil(len(fRows) * topPercentage * 0.01)
            fRows = fRows[:numItems]
            stat = { s : Counter([row[i] for row in fRows]) for s, i in colStatKeys.items() }
            stat = { s : { k : [c, c / numItems * 100] for k, c in count.items() } for s, count in stat.items() }
            stats.append({'filter': f, 'stats': stat, 'rowCount': totalRowCount, 'rowsFiltered': numItems })
            #filtered.append(fRows)
        result.append(stats)
    
    return result

def to_excel(results):
    workbook = openpyxl.Workbook()
    
    # Sheet generator
    def sheet_enumerable():
        yield workbook.active
        while True:
            yield workbook.create_sheet()

    sheetGen = sheet_enumerable()
    for result in results:
        # Get sheet
        sheet = next(sheetGen)

        # Gather the const vars
        catsConst = result['catsConst']
        sheet.title = '_'.join(v[0] for v in catsConst.values())

        # Grab actualr result
        resList = result['result']
        for resItem in resList:
            insertHeader = True
            for res in resItem:

                # Append header
                if insertHeader:
                    header = list(res['filter'].keys()) + list(res['stats'].keys())
                    sheet.append(header)
                    for cell in sheet[sheet.max_row]:
                        cell.font = Font(bold=True)
                    insertHeader = False

                # Append results
                stats = res['stats']
                
                # Get values for const categories
                row = [r[0] for r in res['filter'].values()]

                # Sort values by top percentage scores and add to row-tail 
                r = [dict(sorted(vals.items(), key=lambda x:x[1][0], reverse=True)) for vals in stats.values()]
                rowTail = ['-'.join(['/'.join([str(k), str(round(v[1],2))]) for k,v in obj.items()]) for obj in r]

                # append to sheet
                sheet.append(row + rowTail)
        
            sheet.append([])
        sheet.append([])
        sheet.append([])
    
    workbook.save('stats.xlsx')

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Generate a matrix for top x% results.\n{versionString}')
    parser.add_argument('--result', default='smb/all_results.json', help='The result to load')
    args = parser.parse_args()
    combsLength = 3
    topPercentage = 5

    # Load run data
    print('Loading data')
    resultPath = args.result
    runData = load(resultPath)
    
    # Generate rowData and sort by score
    print('Processing data')
    rowData = RowData(runData)
    scoreIndex = RowData.HEADER.index('score')
    rowData.sort_row_data(scoreIndex)

    catsConst = lambda c: {
        'imageLoader': [ 'gray_tm' ], 
        'metric': [ c ]
    }

    catsVar = {
        'ref-noisy': [], 
        'thresholding': [],
        'search': [],
        'denoiser_coeff': []
    }

    filterDict = rowData.get_filter_dict()
    results = [{'catsConst': catsConst(k), 'filterDict': filterDict, 'result': compute_stats(rowData, catsConst(k), catsVar, topPercentage, combsLength)} for k in ['mse', 'psnr', 'ssim']]

    print('Saving results')
    to_excel(results)
    save('stats.json', results, False)
    print('Done')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()