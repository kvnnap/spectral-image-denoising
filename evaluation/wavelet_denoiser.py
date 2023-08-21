import numpy as np
import copy
import pywt
from utils.image import *
from skopt.space import Real
from denoiser import Denoiser

class WaveletDenoiser(Denoiser):
    def __init__(self):
        self.wavelet_name = 'sym2'
        self.level = 0

    @staticmethod
    def filter_coeffs(coeffs, x, thresholding):
        c = 0
        for i in range(1, len(coeffs)):
            for img in coeffs[i]:
                tImg = thresholding(img, x[c])
                img[True] = tImg
                c += 1

    # need to parameterise wavelet_name, level, masking type (soft, hard)
    def run(self, denoiserParams):
        ref_image = load_image(denoiserParams.pairImage[0])
        image = load_image(denoiserParams.pairImage[1])

        level = pywt.dwtn_max_level(image.shape, self.wavelet_name) if (self.level == 0) else self.level
        coeffs = pywt.wavedec2(image, self.wavelet_name, level=level)

        std = []
        for i in range(1, len(coeffs)):
            for hvd in coeffs[i]: #hor,ver,diag
                std.append(np.std(hvd))

        # Define the search space
        space = list(map(lambda x: Real(0, x), std))

        def objective_function(x):
            coeffCopy = copy.deepcopy(coeffs)
            WaveletDenoiser.filter_coeffs(coeffCopy, x, denoiserParams.thresholding)
            filtered_img = pywt.waverec2(coeffCopy, self.wavelet_name)
            score = denoiserParams.metric(ref_image, filtered_img)
            return score

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        level = pywt.dwtn_max_level(image.shape, self.wavelet_name) if (self.level == 0) else self.level
        coeffs = pywt.wavedec2(image, self.wavelet_name, level=level)
        WaveletDenoiser.filter_coeffs(coeffs, coeff, thresholding)
        return pywt.waverec2(coeffs, self.wavelet_name)
    def get_ceoff_image(self, image, coeff):
        return None

