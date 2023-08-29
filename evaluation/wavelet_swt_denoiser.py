import numpy as np
import copy
import pywt
from utils.image import *
from skopt.space import Real
from denoiser import Denoiser

class WaveletSwtDenoiser(Denoiser):
    def __init__(self, config):
        super().__init__()
        self.waveletName = config['waveletName'] if 'waveletName' in config else 'sym2'
        self.level = config['level'] if 'level' in config else 0

    @staticmethod
    def filter_coeffs(coeffs, x, thresholding):
        coeffs = copy.deepcopy(coeffs)
        c = 0
        for coeff in coeffs:
            for img in coeff[1]:
                tImg = thresholding.fn(img, x[c])
                img[True] = tImg
                c += 1
        return coeffs

    # need to parameterise wavelet_name, level, masking type (soft, hard)
    def run(self, denoiserParams):
        ref_image = load_image(denoiserParams.pairImage[0])
        orig_shape = ref_image.shape
        new_shape = next_power_of_two(max(ref_image.shape))
        new_shape = (new_shape, new_shape)
        ref_image = crop_enlarge(ref_image, new_shape)
        ref_image = crop_enlarge(ref_image, orig_shape)

        image = load_image(denoiserParams.pairImage[1])
        image = crop_enlarge(image, new_shape)
        #image = crop_enlarge(image, orig_shape)

        level = pywt.swt_max_level(max(image.shape)) if (self.level == 0) else self.level
        coeffs = pywt.swt2(image, self.waveletName, level=level)

        measure = []
        for c in coeffs:
            for hvd in c[1]:
                measure.append(np.std(hvd))

        # Define the search space
        space = denoiserParams.thresholding.get_space(measure)

        def objective_function(x):
            coeffCopy = WaveletSwtDenoiser.filter_coeffs(coeffs, x, denoiserParams.thresholding)
            filtered_img = pywt.iswt2(coeffCopy, self.waveletName)
            filtered_img = crop_enlarge(filtered_img, orig_shape)
            score = denoiserParams.metric(ref_image, filtered_img)
            return score

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        level = pywt.swt_max_level(image.shape, self.waveletName) if (self.level == 0) else self.level
        coeffs = pywt.swt2(image, self.waveletName, level=level)
        coeffs = WaveletSwtDenoiser.filter_coeffs(coeffs, coeff, thresholding)
        filtered_img = pywt.iswt2(coeffs, self.waveletName)
        filtered_img = crop_enlarge(filtered_img, image.shape)
        return filtered_img
    def get_ceoff_image(self, image, coeff):
        return None

