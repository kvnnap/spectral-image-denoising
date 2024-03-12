import tkinter as tk
from tkinter import filedialog
from visualisation.result_image_processor import ResultImageProcessor
from visualisation.result_plot import ResultPlot
from utils.image import save_image
from utils.image import interpolate_image_to_range

# parent is the tk sheet
class RunViewer():
    def __init__(self, parent, run):
        dp = run.denoiserParams
        
        self.imgLoaderStr = dp.imageLoader
        toneMapped = self.imgLoaderStr.endswith('_tm')
        if toneMapped:
            self.imgLoaderStr = self.imgLoaderStr[:-3]

        self.id = dp.id
        self.run = run
        self.resImageProc = ResultImageProcessor(run) #run.denoiserResult.func_vals
        self.currentCoeffId = None
        self.backImage = None
        self.isClosing = False
        self.isLoading = False

        self.parentResultViewer = parent
        self.subWindow = tk.Toplevel(parent)
        self.subWindow.title(f"Run ID: {self.id}")
        self.subWindow.protocol("WM_DELETE_WINDOW", self.closing_window)
        self.subWindow.bind("<Destroy>", self.closing_window)

        self.resultPlot = ResultPlot(self)

        self.toneMap = tk.IntVar(value=toneMapped)
        self.toneMapCheckbox = tk.Checkbutton(self.subWindow, text='Tone Map', variable=self.toneMap, command=self.tone_map)
        self.toneMapCheckbox.pack()

        self.showCoeff = tk.IntVar()
        self.showCoeffButton = tk.Checkbutton(self.subWindow, text='Show Coefficients', variable=self.showCoeff, command=self.show_coeffs)
        self.showCoeffButton.pack()

        self.applyButton = tk.Button(self.subWindow, text='Apply Coeffs on Other Image', command=self.apply_on_other_image)
        self.applyButton.pack()

        self.applyBgButton = tk.Button(self.subWindow, text='Apply Background Image', command=self.apply_background_image)
        self.applyBgButton.pack()

        self.changeRefImageButton = tk.Button(self.subWindow, text='Change Reference Image', command=self.change_reference_image)
        self.changeRefImageButton.pack()

        self.saveImagesButton = tk.Button(self.subWindow, text='Save Images', command=self.save_images)
        self.saveImagesButton.pack()

        self.mseLabel = tk.Label(self.subWindow, text='MSE: 0')
        self.mseLabel.pack()

        self.ssimLabel = tk.Label(self.subWindow, text='SSIM: 0')
        self.ssimLabel.pack()

        self.psnrLabel = tk.Label(self.subWindow, text='PSNR: 0')
        self.psnrLabel.pack()

        self.hdrvdpLabel = tk.Label(self.subWindow, text='HDRVDP3: 0')
        self.hdrvdpLabel.pack()

        self.uiCollection = [self.toneMapCheckbox, self.showCoeffButton, self.applyButton, self.applyBgButton, self.changeRefImageButton, self.saveImagesButton]

        self.plot()

    def plot(self):
        self.toggle_loading()
        (image, denImage, coeffImage) = self.resImageProc.get(self.showCoeff.get(), self.currentCoeffId)
        if (self.backImage is not None):
            image = self.backImage + image
            denImage = self.backImage + denImage
        self.plot_raw(coeffImage, image, denImage)
        scores = self.resImageProc.compute_score(self.currentCoeffId)
        self.mseLabel.config(text=f"MSE: { scores['mse'] }")
        self.ssimLabel.config(text=f"SSIM: { scores['ssim'] }")
        self.psnrLabel.config(text=f"PSNR: { scores['psnr'] }")
        self.hdrvdpLabel.config(text=f"HDRVDP3: { scores['hdrvdp3'] }")
        self.toggle_loading()
    
    def plot_raw(self, coeffImage, image, denImage):
        self.resultPlot.plot_result(self.run.denoiserResult.func_vals, coeffImage, image, denImage)

    def toggle_loading(self):
        self.isLoading = not self.isLoading
        loadingMessage = f"Run ID: {self.id}"
        if self.isLoading:
            loadingMessage = loadingMessage + " - Loading"
        self.subWindow.title(loadingMessage)
        for uiElement in self.uiCollection:
            uiElement['state'] = tk.DISABLED if self.isLoading else tk.NORMAL
        self.parentResultViewer.toggle_loading()

    def tone_map(self):
        imgLoaderStr = self.imgLoaderStr 
        if self.toneMap.get():
            imgLoaderStr = imgLoaderStr + '_tm'
        self.resImageProc.update_image_loader(imgLoaderStr)
        self.plot()

    def show_coeffs(self):
        self.plot()

    def change_coeff(self, coeffId):
        if coeffId < 0 or coeffId >= len(self.run.denoiserResult.x_iters):
            print('Out of range')
            return
        self.currentCoeffId = coeffId
        self.plot()

    # Move logic here
    def apply_on_other_image(self):
        fileName = filedialog.askopenfilename(parent=self.subWindow, title='Select RAW file')
        self.resImageProc.update_image_path(fileName)
        self.plot()

    def apply_background_image(self):
        fileName = filedialog.askopenfilename(parent=self.subWindow, title='Select RAW file')
        self.backImage = self.resImageProc.get_image(fileName)
        self.plot()

    def change_reference_image(self):
        fileName = filedialog.askopenfilename(parent=self.subWindow, title='Select RAW file')
        self.resImageProc.update_ref_image_path(fileName)
        self.plot()

    def save_images(self):
        self.toggle_loading()
        (image, denImage, coeffImage) = self.resImageProc.get(self.showCoeff.get(), self.currentCoeffId)
        dp = self.run.denoiserParams
        #full_name = f'{dp.name}-{dp.id}-{dp.denoiser["name"]}_{dp.denoiser["coefficientLength"]}-{dp.search}-{dp.thresholding}-{dp.imageLoader}-{dp.metric}-{dp.iterations}'
        name = f'{dp.name}-{dp.id}'
        dir_name = 'screenshots'
        path = f'{dir_name}/{name}'
        save_image(image, f'{path}-noisy')
        save_image(denImage, f'{path}-denoised')
        if self.showCoeff.get():
            save_image(interpolate_image_to_range(coeffImage), f'{path}-coefficients')
        plotImage = self.resultPlot.plot_to_image(self.run.denoiserResult.func_vals)
        save_image(interpolate_image_to_range(plotImage), f'{path}-plot')
        self.toggle_loading()

    def closing_window(self, event = None):
        if self.isClosing:
            return
        self.isClosing = True
        self.resultPlot.destroy()
        self.subWindow.destroy()