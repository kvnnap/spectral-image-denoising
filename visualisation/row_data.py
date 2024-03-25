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
    def to_rows(runData, filterDict):
        row = []
        scoreIndex = RowData.HEADER.index('score')
        iterIndex = RowData.HEADER.index('iter')
        timeIndex = RowData.HEADER.index('time')
        messageIndex = RowData.HEADER.index('message')
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
        return row
    
    def __init__(self, runData):
        self.runData = runData
        self.filterDict = { key: set() for key in RowData.HEADER if key not in RowData.FILTER_FROM_DICT }
        self.rowData = RowData.to_rows(runData, self.filterDict)
        # Only filter categories with more than 1 item
        self.filterDict = {k: v for k, v in self.filterDict.items() if len(v) > 1}

    def sort_row_data(self, columnId, reverse=False):
        self.rowData.sort(key=lambda row: row[columnId], reverse=reverse)

    def get_run_data(self):
        return self.runData
    
    def get_row_data(self):
        return self.rowData

    def get_filter_dict(self):
        return self.filterDict
    
    def filter_rows(self, filters):
        return RowData.filter_data(self.rowData, filters)
    
    