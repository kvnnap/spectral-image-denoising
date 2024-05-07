import copy
import curvelops as cl
from evaluation.denoiser import Denoiser
from utils.array import sanitise
from utils.image import *
from utils.math import get_threshold_max
import matplotlib as mpl
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from curvelops.plot import (
    create_inset_axes_grid,
    create_axes_grid,
    overlay_disks,
)

class CurveletDenoiser(Denoiser):
    def __init__(self, config):
        super().__init__()
        self.computeSectors = config['sectors'] if 'sectors' in config else False
        
    @staticmethod
    def get_fdct_struct(c_str, x, thresholding, computeSectors):
        sectorCounter = 0
        c_copy = copy.deepcopy(c_str)
        for c_struct in c_copy:
            for i, s in enumerate(c_struct):
                for j in range(len(s)):
                    c_struct[i][j] = thresholding.fn(c_struct[i][j], x[sectorCounter] if computeSectors else x[i])
                    sectorCounter += 1
        return c_copy
    
    def decompose(self, image, nbscales = None):
        FDCT = cl.FDCT2D(dims=image.shape[:2], nbscales=nbscales)
        c_struct = list(map(lambda x: FDCT.struct(FDCT @ x), seperate_channels(image)))
        return (FDCT, c_struct)
    
    def recompose(self, FDCT, c_struct):
        return merge_channels(list(map(lambda x: sanitise((FDCT.H @ (FDCT.vect(x))).real), c_struct)))
    
    # need to parameterise wavelet_name, level, masking type (soft, hard)
    def run(self, denoiserParams, dpString):
        ref_image = denoiserParams.imageLoaderMethod(denoiserParams.pairImage[0])
        image = denoiserParams.imageLoaderMethod(denoiserParams.pairImage[1])

        FDCT, c_struct = self.decompose(image)

        measure = []
        if self.computeSectors:
            for i in range(len(c_struct[0])):
                for j in range(len(c_struct[0][i])):
                    wedges_flattened = []
                    for c in range(len(c_struct)):
                        wedges_flattened.extend(c_struct[c][i][j].flatten())
                    measure.append(get_threshold_max(wedges_flattened))
        else:
            for i in range(len(c_struct[0])):
                wedges_flattened = []
                for j in range(len(c_struct[0][i])):
                    for c in range(len(c_struct)):
                        wedges_flattened.extend(c_struct[c][i][j].flatten())
                measure.append(get_threshold_max(wedges_flattened))

        space = denoiserParams.thresholding.get_space(measure)

        def objective_function(x):
            c_copy = CurveletDenoiser.get_fdct_struct(c_struct, x, denoiserParams.thresholding, self.computeSectors)
            score = denoiserParams.metric(ref_image, self.recompose(FDCT, c_copy), dpString)
            return score

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    
    def get_image(self, image, coeff, thresholding):
        FDCT, c_struct = self.decompose(image)
        c_struct = CurveletDenoiser.get_fdct_struct(c_struct, coeff, thresholding, self.computeSectors)
        return self.recompose(FDCT, c_struct)
    
    def get_curve_ceoff_image(self, image, coeff, thresholding):
        if (get_channel_count(image) > 1):
            image = convert_to_grayscale(image)
        image = image[:, :, 0]
        #image = image.T
        FDCT, c_struct = self.decompose(image)
        c_struct = CurveletDenoiser.get_fdct_struct(c_struct, coeff, thresholding, self.computeSectors)
        c_struct = c_struct[0]

        rows, cols = 2, 3
        plt.ioff()
        fig, ax = plt.subplots()
        ax.imshow(
            image.T, cmap="gray"
        )
        axesin = create_inset_axes_grid(
            ax, rows, cols, width=0.4, kwargs_inset_axes=dict(projection="polar")
        )
        overlay_disks(c_struct, axesin, linewidth=0.0, cmap="turbo")

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        mpl.colorbar.ColorbarBase(
            cax, cmap="turbo", norm=mpl.colors.Normalize(vmin=0, vmax=1)
        )
        
        fig.canvas.draw()
        image_data = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image_data = image_data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        plt.close(fig)
        plt.ion()
        return image_data

    def get_curve_ceoff_whole_image(self, image, coeff, thresholding):
        FDCT = cl.FDCT2D(dims=image.shape[:2], nbscales=None)

        # Optimisation to avoid decomposing the image again, we only need a look-alike structure
        c_struct = [[np.zeros(s) for s in shape] for shape in FDCT.shapes]

        sectorCounter = 0
        for scale_index, scale in enumerate(c_struct):
            for wedge_index in range(len(scale)):
                # c_struct[scale_index][wedge_index] = np.full_like(c_struct[scale_index][wedge_index], count)
                c_index = sectorCounter if self.computeSectors else scale_index
                c_struct[scale_index][wedge_index] = np.full((1, 1), complex(coeff[c_index]))
                sectorCounter += 1
                #c_struct[scale_index][wedge_index] = count

        plt.ioff()

        rows, cols = 1, 1
        fig, axes = create_axes_grid(
            rows,
            cols,
            kwargs_subplots=dict(projection="polar"),
            kwargs_figure=dict(figsize=(4, 4)),
        )
        overlay_disks(c_struct, axes, annotate=False, cmap='gray')

        fig.canvas.draw()
        image_data = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image_data = image_data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        plt.close(fig)
        
        plt.ion()
        return image_data

    def get_ceoff_image(self, image, coeff, thresholding):
        return self.get_curve_ceoff_whole_image(image, coeff, thresholding)
        #return list_to_square_image(coeff)
