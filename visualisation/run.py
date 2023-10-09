import sys
import os
import math
import argparse
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

from tksheet import Sheet
from functools import partial
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.denoiser_factory import DenoiserFactory
from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import MetricFactory
from evaluation.thresholds import ThresholdFactory

from utils.versioning import get_version
from utils.serialisation import to_string_obj, load, print_obj

class ResultImageProcessor():
    def __init__(self, run):
        dp = run.denoiserParams
        self.run = run
        self.imageLoaderMethod = ImageLoaderFactory.create(dp.imageLoader)
        self.thresholdMethod = ThresholdFactory.create(dp.thresholding)
        self.denoiserMethod = DenoiserFactory.create(dp.denoiser)
        self.image = self.imageLoaderMethod(dp.pairImage[1])
    
    def get(self, renderCoeffImage = True, coeffId = None):
        coeffs = self.run.denoiserResult.x if coeffId is None else self.run.denoiserResult.x_iters[coeffId]
        den = self.denoiserMethod.get_image(self.image, coeffs, self.thresholdMethod)
        den_coeff = None
        if (renderCoeffImage):
            den_coeff = self.denoiserMethod.get_ceoff_image(self.image, coeffs, self.thresholdMethod)
        return (self.image, den, den_coeff)
    
    def update_image_path(self, path):
        self.image = self.imageLoaderMethod(path)

class ResultViewer(tk.Tk):
    def __init__(self, runData):
        tk.Tk.__init__(self)

        # process data to rows/cols
        header = ['id', 'name', 'imageLoader', 'metric', 'score', 'thresholding', 'search', 'iterations', 'denoiser', 'denoiser_coeff']
        row = []
        for run in runData.runs:
            dp = run.denoiserParams
            row.append([
                dp.id,
                dp.name,
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
        self.loading = False
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
        self.sheet.enable_bindings('toggle_select', 'single_select', 'row_select', 'column_select', 'right_click_popup_menu', 'column_width_resize')
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

    def toggle_loading(self):
        self.loading = not self.loading
        if self.loading:
            self.title('Result Explorer - Loading')
        else:
            self.title('Result Explorer')
        self.update()

    def show_run(self, rowId):
        if (self.loading):
            return
        
        # subWindow = tk.Toplevel(self)
        # subWindow.title('Test')
        # subWindow.protocol("WM_DELETE_WINDOW", subWindow.destroy)
        # subWindow.destroy()

        # get run_Id from row_id
        runId = self.sheet.get_cell_data(rowId, 0)
        run = next((x for x in self.runData.runs if x.denoiserParams.id == runId), None)
        if run is None:
            return
        self.toggle_loading()

        resImageProc = ResultImageProcessor(run)
        (image, denImage, coeffImage) = resImageProc.get(self.renderCoeff)

        fig = plt.figure()
        # canvas = FigureCanvasTkAgg(fig, master=subWindow)
        # canvas.get_tk_widget().pack()

        ax = np.array([[fig.add_subplot(2, 2, 1), fig.add_subplot(2, 2, 2)], [fig.add_subplot(2, 2, 3), None]])
        ax[1, 1] = fig.add_subplot(2, 2, 4, sharex=ax[1, 0], sharey=ax[1, 0])

        ax[0, 0].plot(run.denoiserResult.func_vals)
        ax[1, 0].imshow(image)
        if coeffImage is not None: ax[0, 1].imshow(coeffImage)
        ax[1, 1].imshow(denImage)

        def show_coeff(event):
            if event.inaxes == ax[0, 1]:
                self.renderCoeff = not self.renderCoeff
            
            if event.inaxes == ax[1, 1]:
                fileName = filedialog.askopenfilename(parent=self, title='Select RAW file')
                resImageProc.update_image_path(fileName)

            if event.inaxes == ax[0, 0]:
                if (self.loading):
                    return
                
                coeffId = math.floor(event.xdata)
                if coeffId < 0 or coeffId >= len(run.denoiserResult.x_iters):
                    print('Out of range')
                    return
                
                self.toggle_loading()
                fig.canvas.manager.set_window_title('Loading')
                fig.canvas.flush_events()

                (image, denoisedImage, coeffImage) = resImageProc.get(self.renderCoeff, coeffId)
                ax[1, 0].imshow(image)
                if coeffImage is not None: ax[0, 1].imshow(coeffImage)
                ax[1, 1].imshow(denoisedImage)
                plt.draw()

                fig.canvas.manager.set_window_title('Ok')
                self.toggle_loading()
                
        fig.canvas.mpl_connect('button_press_event', show_coeff)
        plt.tight_layout()
        self.toggle_loading()
        plt.show()

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Visualises results produced by evaluation/run.py.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='Where to load the JSON RunData object from')
    args = parser.parse_args()
    resultPath = args.result
    runData = load(resultPath)
    app = ResultViewer(runData)
    app.mainloop()
    
# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()