import sys
import os
import argparse
import tkinter as tk

from tksheet import Sheet
from functools import partial

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load
from utils.math import euclidean_distance
from utils.image import set_base_path

from visualisation.run_viewer import RunViewer

class ResultViewer(tk.Tk):
    def __init__(self, runData):
        tk.Tk.__init__(self)

        # process data to rows/cols
        self.header = ['id', 'name', 'ref-noisy', 'imageLoader', 'metric', 'score', 'thresholding', 'search', 'iterations', 'denoiser', 'denoiser_coeff', 'sample']
        self.filterDict = { key: set() for key in self.header if not(key in ['id', 'score']) }
        row = []
        scoreIndex = self.header.index('score')
        for run in runData.runs:
            dp = run.denoiserParams
            for key in self.filterDict:
                self.filterDict[key].update({ dp.get_value(key) })
            rowItem = [dp.get_value(val) for val in self.header]
            rowItem[scoreIndex] = run.denoiserResult.fun
            row.append(rowItem)
        
        # Only filter categories with more than 1 item
        self.filterDict = {k: v for k, v in self.filterDict.items() if len(v) > 1}
        
        # continue
        self.title('Result Explorer')
        self.isLoading = False
        self.runData = runData
        self.rowData = row
        self.renderCoeff = False
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)
        self.frame = tk.Frame(self)
        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_rowconfigure(0, weight = 1)
        self.sheet = Sheet(self.frame, data = row, header=self.header)
        self.sheet.enable_bindings('toggle_select', 'single_select', 'ctrl_select', 'row_select', 'column_select', 'right_click_popup_menu', 'column_width_resize')
        self.sheet.popup_menu_add_command("sort asc", partial(self.sort, False))
        self.sheet.popup_menu_add_command("sort desc", partial(self.sort, True))
        self.sheet.extra_bindings([('all_select_events', self.row_select)])
        self.frame.grid(row = 0, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")

        self.cmpButton = tk.Button(self.frame, text='Compare', command=self.compare_coeff)
        self.cmpButton.grid(row = 1, column = 0, sticky='w')

        self.label = tk.Label(self.frame, text='0')
        self.label.grid(row = 1, column = 0, sticky='e')

        # Checkboxes?
        self.checkboxFrame = tk.Frame(self.frame)
        self.checkboxFrame.grid(row=2, column=0)
        self.filterValues = {}
        if len(self.filterDict) > 0:
            for i, key in enumerate(self.filterDict.keys()):
                group_frame = tk.LabelFrame(self.checkboxFrame, text=key)
                group_frame.grid(row=0, column=i)
                self.filterValues[key] = []
                for j, f in enumerate(sorted(self.filterDict[key])):
                    ck_var = tk.BooleanVar()
                    ck = tk.Checkbutton(group_frame, text=f, variable=ck_var)
                    if key == 'ref-noisy' or key == 'denoiser_coeff':
                        ck.grid(row=j//2, column=j % 2)
                    else:
                        ck.grid(row=j, column=0)
                    self.filterValues[key].append((f, ck_var))
            self.filterButton = tk.Button(self.checkboxFrame, text='Apply', command=self.apply_filter)
            self.filterButton.grid(row=0, column=i+1)

    def apply_filter(self):
        filters = {}
        for key, listValues in self.filterValues.items():
            filters[key] = [val_name for val_name, ck_var in listValues if ck_var.get()]
        filters = { key: val for key, val in filters.items() if val }
        self.filter_data(filters)

    def sort(self, reverse=False, event = None):
        columnId = self.sheet.get_selected_columns().pop()
        self.rowData.sort(key=lambda row: row[columnId], reverse=reverse)
        self.apply_filter()

    def filter_data(self, filters):
        def condition(row):
            AndResult = True
            for name, listValues in filters.items():
                if not listValues:
                    continue
                rowIndex = self.header.index(name)
                OrResult = False
                for value in listValues:
                    OrResult |= row[rowIndex] == value
                    if OrResult:
                        break
                AndResult &= OrResult
                if AndResult == False:
                    break
            return AndResult
        filtered_data = list(filter(condition, self.rowData))
        self.sheet.set_sheet_data(filtered_data)

    def row_select(self, event = None):
        if event[0] == 'select_row':
            self.show_run(event[1])

    def toggle_loading(self):
        self.isLoading = not self.isLoading
        if self.isLoading:
            self.title('Result Explorer - Loading')
        else:
            self.title('Result Explorer')
        self.update()

    def get_run_from__row_id(self, rowId):
        runId = self.sheet.get_cell_data(rowId, 0)
        return next((x for x in self.runData.runs if x.denoiserParams.id == runId), None)
        
    def show_run(self, rowId):
        if (self.isLoading):
            return

        # get run_Id from row_id
        run = self.get_run_from__row_id(rowId)
        if run is None:
            return
        
        rv = RunViewer(self, run)

    def compare_coeff(self):
        cells = self.sheet.get_selected_cells()
        if len(cells) != 2:
            return
        rows = list(map(lambda cell: self.get_run_from__row_id(cell[0]).denoiserResult.x, cells))
        result = euclidean_distance(rows[0], rows[1])
        self.label.config(text=f"{result}")
        
def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Visualises results produced by evaluation/run.py.\n{versionString}')
    parser.add_argument('--result', help='Where to load the JSON RunData object from', action='append')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    args = parser.parse_args()
    resultPath = args.result
    if not resultPath:
        resultPath = ['result.json']
    set_base_path(args.image_base)
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
    app = ResultViewer(runData)
    app.mainloop()
    
# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()