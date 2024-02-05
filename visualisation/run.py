import sys
import os
import argparse
import tkinter as tk

from tksheet import Sheet
from functools import partial

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import to_string_obj, load
from utils.string import extract_file_name
from utils.math import euclidean_distance
from utils.image import set_base_path

from visualisation.run_viewer import RunViewer

class ResultViewer(tk.Tk):
    def __init__(self, runData):
        tk.Tk.__init__(self)

        # process data to rows/cols
        header = ['id', 'name', 'ref-noisy', 'imageLoader', 'metric', 'score', 'thresholding', 'search', 'iterations', 'denoiser', 'denoiser_coeff']
        row = []
        for run in runData.runs:
            dp = run.denoiserParams
            row.append([
                dp.id,
                dp.name,
                f"{extract_file_name(dp.pairImage[0])}-{extract_file_name(dp.pairImage[1])}",
                dp.imageLoader,
                dp.metric,
                run.denoiserResult.fun,
                dp.thresholding,
                dp.search,
                dp.iterations,
                dp.denoiser['name'] if 'name' in dp.denoiser else dp.denoiser,
                to_string_obj(dp.denoiser)
            ])
        
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
        self.sheet = Sheet(self.frame,
                           data = row, header=header)
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

    def sort(self, reverse=False, event = None):
        columnId = self.sheet.get_selected_columns().pop()
        self.rowData.sort(key=lambda row: row[columnId], reverse=reverse)
        self.sheet.set_sheet_data(self.rowData)

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
    parser.add_argument('--result', default='result.json', help='Where to load the JSON RunData object from')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    args = parser.parse_args()
    resultPath = args.result
    set_base_path(args.image_base)
    runData = load(resultPath)
    app = ResultViewer(runData)
    app.mainloop()
    
# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()