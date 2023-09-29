import sys
import os
import math
import argparse
import matplotlib.pyplot as plt
import tkinter as tk

from tksheet import Sheet
from functools import partial

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.denoiser_factory import DenoiserFactory
from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import MetricFactory
from evaluation.thresholds import ThresholdFactory

from utils.versioning import get_version
from utils.serialisation import to_string_obj, load, print_obj

class demo(tk.Tk):
    def __init__(self, runData):
        tk.Tk.__init__(self)

        # process data to rows/cols
        header = ['id', 'name', 'imageLoader', 'metric', 'thresholding', 'search', 'iterations', 'denoiser', 'denoiser_coeff']
        row = []
        for run in runData.runs:
            dp = run.denoiserParams
            row.append([
                dp.id,
                dp.name,
                dp.imageLoader,
                dp.metric,
                dp.thresholding,
                dp.search,
                dp.iterations,
                dp.denoiser['name'] if 'name' in dp.denoiser else dp.denoiser,
                to_string_obj(dp.denoiser)
            ])
        
        # continue
        self.runData = runData
        self.rowData = row
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)
        self.frame = tk.Frame(self)
        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_rowconfigure(0, weight = 1)
        self.sheet = Sheet(self.frame,
                           data = row, header=header)
        self.sheet.enable_bindings('toggle_select', 'single_select', 'row_select', 'column_select', 'right_click_popup_menu')
        self.sheet.popup_menu_add_command("sort asc", partial(self.sort, False))
        self.sheet.popup_menu_add_command("sort desc", partial(self.sort, True))
        self.sheet.extra_bindings([('all_select_events', self.row_select)])
        self.frame.grid(row = 0, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")

    def sort(self, reverse=False, event = None):
        columnId = self.sheet.get_selected_columns().pop()
        self.rowData.sort(key=lambda row: row[columnId], reverse=reverse)
        self.sheet.set_sheet_data(self.rowData)

    def row_select(self, event = None):
        if event[0] == 'select_row':
            self.show_run(event[1])

    def show_run(self, rowId):
        # get run_Id from row_id
        runId = self.sheet.get_cell_data(rowId, 0)
        run = next((x for x in self.runData.runs if x.denoiserParams.id == runId), None)
        if run is None:
            return
        
        dp = run.denoiserParams

        pairImage = dp.pairImage
        imageLoaderMethod = ImageLoaderFactory.create(dp.imageLoader)
        thresholdMethod = ThresholdFactory.create(dp.thresholding)
        denoiserMethod = DenoiserFactory.create(dp.denoiser)

        image = imageLoaderMethod(pairImage[1])
        
        fig, ax = plt.subplots(2, 2)
        ax[0, 0].plot(run.denoiserResult.func_vals)
        coeffImage = denoiserMethod.get_ceoff_image(image, run.denoiserResult.x)
        if coeffImage is not None:
            ax[0, 1].imshow(coeffImage)
        ax[1, 0].imshow(imageLoaderMethod(pairImage[0]))
        ax[1, 1].imshow(denoiserMethod.get_image(image, run.denoiserResult.x, thresholdMethod))
        def test(event):
            if event.inaxes == ax[0, 0]:
                x = math.floor(event.xdata)
                if x < 0 or x >= len(run.denoiserResult.x_iters):
                    print('Out of range')
                    return
                coeffImage = denoiserMethod.get_ceoff_image(image, run.denoiserResult.x_iters[x])
                denoisedImage = denoiserMethod.get_image(image, run.denoiserResult.x_iters[x], thresholdMethod)
                if coeffImage is not None:
                    ax[0, 1].imshow(coeffImage)
                ax[1, 1].imshow(denoisedImage)
                plt.draw()
                print(x)
        fig.canvas.mpl_connect('button_press_event', test)
        plt.tight_layout()
        plt.show()

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Visualises results produced by evaluation/run.py.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='Where to load the JSON RunData object from')
    args = parser.parse_args()
    resultPath = args.result
    runData = load(resultPath)
    app = demo(runData)
    app.mainloop()
    
# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()