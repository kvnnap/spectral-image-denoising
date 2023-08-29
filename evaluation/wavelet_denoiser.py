import numpy as np
import copy
import pywt
from utils.image import *
from skopt.space import Real
from denoiser import Denoiser

class WaveletDenoiser(Denoiser):
    def __init__(self, config):
        super().__init__()
        self.waveletName = config['waveletName'] if 'waveletName' in config else 'sym2'
        self.level = config['level'] if 'level' in config else 0

    @staticmethod
    def filter_coeffs(coeffs, x, thresholding):
        c = 0
        for i in range(1, len(coeffs)):
            for img in coeffs[i]:
                tImg = thresholding.fn(img, x[c])
                img[True] = tImg
                c += 1

    # need to parameterise wavelet_name, level, masking type (soft, hard)
    def run(self, denoiserParams):
        ref_image = load_image(denoiserParams.pairImage[0])
        image = load_image(denoiserParams.pairImage[1])

        level = pywt.dwtn_max_level(image.shape, self.waveletName) if (self.level == 0) else self.level
        coeffs = pywt.wavedec2(image, self.waveletName, level=level)

        measure = []
        for i in range(1, len(coeffs)):
            for hvd in coeffs[i]: #hor,ver,diag
                measure.append(np.std(hvd))

        # Define the search space
        space = denoiserParams.thresholding.get_space(measure)

        def objective_function(x):
            coeffCopy = copy.deepcopy(coeffs)
            WaveletDenoiser.filter_coeffs(coeffCopy, x, denoiserParams.thresholding)
            filtered_img = pywt.waverec2(coeffCopy, self.waveletName)
            score = denoiserParams.metric(ref_image, filtered_img)
            return score

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        level = pywt.dwtn_max_level(image.shape, self.waveletName) if (self.level == 0) else self.level
        coeffs = pywt.wavedec2(image, self.waveletName, level=level)
        WaveletDenoiser.filter_coeffs(coeffs, coeff, thresholding)
        return pywt.waverec2(coeffs, self.waveletName)
    def get_ceoff_image(self, image, coeff):
        return None

