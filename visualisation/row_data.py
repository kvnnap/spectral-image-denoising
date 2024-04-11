from functools import cmp_to_key

class RowData():
    HEADER = ['id', 'name', 'ref-noisy', 'imageLoader', 'metric', 'score', 'thresholding', 'search', 'iterations', 'iter', 'denoiser', 'denoiser_coeff', 'sample', 'time', 'message']
    FILTER_FROM_DICT = ['id', 'score', 'sample', 'iter', 'time', 'message']

    @staticmethod
    def filter_data(rowData, filters):
        def condition(row):
            AndResult = True
            for name, listValues in filters.items():
                if not listValues:
                    continue
                rowIndex = RowData.HEADER.index(name)
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

    @staticmethod
    def to_rows(runData):
        row = []
        scoreIndex = RowData.HEADER.index('score')
        iterIndex = RowData.HEADER.index('iter')
        timeIndex = RowData.HEADER.index('time')
        messageIndex = RowData.HEADER.index('message')
        filterDict = { key: set() for key in RowData.HEADER if key not in RowData.FILTER_FROM_DICT }
        for run in runData.runs:
            dp = run.denoiserParams
            for key in filterDict:
                filterDict[key].update({ dp.get_value(key) })
            rowItem = [dp.get_value(val) for val in RowData.HEADER]
            rowItem[scoreIndex] = run.denoiserResult.fun
            rowItem[iterIndex] = len(run.denoiserResult.func_vals)
            rowItem[timeIndex] = round(run.time * 1e-9)
            rowItem[messageIndex] = run.denoiserResult.message if hasattr(run.denoiserResult, 'message') else ''
            row.append(rowItem)
        for k, v in filterDict.items():
            filterDict[k] = sorted(v)
        return (row, filterDict)
    
    def __init__(self, runData):
        self.runData = runData
        self.rowData, self.filterDict = RowData.to_rows(runData)
        # Only filter categories with more than 1 item
        self.filterDict = {k: v for k, v in self.filterDict.items() if len(v) > 1}

    def sort_row_data(self, columnId, reverse=False):
        self.rowData.sort(key=lambda row: row[columnId], reverse=reverse)

    def sort_row_data_metric(self, reverse=False):
        # Check if can sort
        if any(not hasattr(run, 'bestMetricResults') or run.bestMetricResults is None for run in self.runData.runs):
            print('Not all runs have a valid bestMetricResults attribute')
            return
        
        idIndex = RowData.HEADER.index('id')

        # Ensure runs are sorted by id
        runs = sorted(self.runData.runs, key=lambda r: r.denoiserParams.id)

        def cmp(r1, r2):
            r = [r1, r2]
            id = [x[idIndex] for x in r]
            run = [runs[i] for i in id]
            # Compute relative scores
            div = [[v[0] / v[1] if v[1] > 0 else v[1] / v[0] for v in r.bestMetricResults.values()] for r in run]
            # Count the metrics that improved
            cnt = [sum(1 for v in d if v > 1) for d in div]

            # More metrics counted, the better
            if cnt[0] != cnt[1]:
                return cnt[1] - cnt[0]
            
            # If equal, discriminate with sum
            sums = [sum(d) for d in div]
            return sums[1] - sums[0]

        self.rowData.sort(key=cmp_to_key(cmp), reverse=reverse)

    def get_run_data(self):
        return self.runData
    
    def get_row_data(self):
        return self.rowData

    def get_filter_dict(self):
        return self.filterDict
    
    def filter_rows(self, filters):
        return RowData.filter_data(self.rowData, filters)
    
    