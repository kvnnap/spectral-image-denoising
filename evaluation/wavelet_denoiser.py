import numpy as np
import copy
import pywt
from utils.image import *
from denoiser import Denoiser

class WaveletDenoiser(Denoiser):
    def __init__(self, config):
        super().__init__()
        self.waveletName = config['waveletName'] if 'waveletName' in config else 'sym2'
        self.level = config['level'] if 'level' in config else 0

    @staticmethod
    def filter_coeffs(coeffArray, x, thresholding):
        for coeffs in coeffArray:
            c = 0
            for i in range(1, len(coeffs)):
                for img in coeffs[i]:
                    tImg = thresholding.fn(img, x[c])
                    img[True] = tImg
                    c += 1

    def decompose(self, image):
        level = pywt.dwtn_max_level(image.shape[:2], self.waveletName) if (self.level == 0) else self.level
        coeffs = list(map(lambda c: pywt.wavedec2(c, self.waveletName, level=level), seperate_channels(image)))
        return coeffs
    
    def recompose(self, coeffs):
        filtered_img = list(map(lambda c: pywt.waverec2(c, self.waveletName), coeffs))
        return merge_channels(filtered_img)
    
    # need to parameterise wavelet_name, level, masking type (soft, hard)
    def run(self, denoiserParams):
        ref_image = denoiserParams.imageLoaderMethod(denoiserParams.pairImage[0])
        image = denoiserParams.imageLoaderMethod(denoiserParams.pairImage[1])

        coeffs = self.decompose(image)

        measure = []
        for i in range(1, len(coeffs[0])):
            for hvd in np.stack([coeffs[x][i] for x in range(0, len(coeffs))], axis=3): #hor,ver,diag
                measure.append(np.std(hvd))

        # Define the search space
        space = denoiserParams.thresholding.get_space(measure)

        def objective_function(x):
            coeffCopy = copy.deepcopy(coeffs)
            WaveletDenoiser.filter_coeffs(coeffCopy, x, denoiserParams.thresholding)
            filtered_img = self.recompose(coeffCopy)
            score = denoiserParams.metric(ref_image, filtered_img)
            return score

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        coeffs = self.decompose(image)
        WaveletDenoiser.filter_coeffs(coeffs, coeff, thresholding)
        return self.recompose(coeffs)
    def get_ceoff_image(self, image, coeff):
        return None

