import numpy as np
import copy
import pywt
from utils.image import *
from evaluation.denoiser import Denoiser

class WaveletSwtDenoiser(Denoiser):
    def __init__(self, config):
        super().__init__()
        self.waveletName = config['waveletName'] if 'waveletName' in config else 'sym2'
        self.level = config['level'] if 'level' in config else 0

    @staticmethod
    def filter_coeffs(coeffArray, x, thresholding):
        for coeffs in coeffArray:
            c = 0
            for coeff in coeffs:
                for img in coeff[1]:
                    tImg = thresholding.fn(img, x[c])
                    img[True] = tImg
                    c += 1

    def decompose(self, image):
        new_shape = next_power_of_two(max(image.shape))
        new_shape = (new_shape, new_shape)
        image = crop_enlarge(image, new_shape)
        level = pywt.swt_max_level(max(image.shape[:2])) if (self.level == 0) else self.level
        coeffs = list(map(lambda c: pywt.swt2(c, self.waveletName, level=level), seperate_channels(image)))
        return coeffs
    def recompose(self, coeffs):
        filtered_img = list(map(lambda c: pywt.iswt2(c, self.waveletName), coeffs))
        return merge_channels(filtered_img)
    
    # need to parameterise wavelet_name, level, masking type (soft, hard)
    def run(self, denoiserParams):
        ref_image = denoiserParams.imageLoaderMethod(denoiserParams.pairImage[0])
        orig_shape = ref_image.shape
        new_shape = next_power_of_two(max(ref_image.shape))
        new_shape = (new_shape, new_shape)
        ref_image = crop_enlarge(ref_image, new_shape)
        ref_image = crop_enlarge(ref_image, orig_shape)

        image = denoiserParams.imageLoaderMethod(denoiserParams.pairImage[1])
        coeffs = self.decompose(image)

        # np.stack([coeffs[x][i] for x in range(0, len(coeffs))], axis=3)
        measure = []
        for c in range(len(coeffs[0])):
            for hvd in np.stack([coeffs[x][c][1] for x in range(len(coeffs))], axis=3):
                measure.append(np.std(hvd))

        # for coeff in coeffs:
        #     for c in coeff:
        #         for hvd in c[1]:
        #             measure.append(np.std(hvd))

        # Define the search space
        space = denoiserParams.thresholding.get_space(measure)

        def objective_function(x):
            coeffCopy = copy.deepcopy(coeffs)
            WaveletSwtDenoiser.filter_coeffs(coeffCopy, x, denoiserParams.thresholding)
            filtered_img = self.recompose(coeffCopy)
            filtered_img = crop_enlarge(filtered_img, orig_shape)
            score = denoiserParams.metric(ref_image, filtered_img)
            return score

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        coeffs = self.decompose(image)
        WaveletSwtDenoiser.filter_coeffs(coeffs, coeff, thresholding)
        filtered_img = self.recompose(coeffs)
        filtered_img = crop_enlarge(filtered_img, image.shape)
        return filtered_img
    def get_ceoff_image(self, image, coeff, thresholding):
        return list_to_square_image(coeff)

