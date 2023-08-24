import copy
import curvelops as cl
from utils.image import *
from skopt.space import Real
from denoiser import Denoiser

class CurveletDenoiser(Denoiser):
    def __init__(self, config):
        super().__init__()
        
    @staticmethod
    def get_fdct_struct(c_str, x, thresholding):
        c_copy = copy.deepcopy(c_str)
        for i, s in enumerate(c_copy):
            for j, w in enumerate(s):
                c_copy[i][j] = thresholding(c_copy[i][j], x[i])
        return c_copy

    # need to parameterise wavelet_name, level, masking type (soft, hard)
    def run(self, denoiserParams):
        ref_image = load_image(denoiserParams.pairImage[0])
        image = load_image(denoiserParams.pairImage[1])


        FDCT = cl.FDCT2D(dims=image.shape)
        coeffs = FDCT @ image
        c_struct = FDCT.struct(coeffs)

        std = []
        for i, s in enumerate(c_struct):
            std.append(5)
        space = list(map(lambda x: Real(0, x), std))

        def objective_function(x):
            c_copy = CurveletDenoiser.get_fdct_struct(c_struct, x, denoiserParams.thresholding)
            score = denoiserParams.metric(ref_image, (FDCT.H @ (FDCT.vect(c_copy))).real)
            return score

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        FDCT = cl.FDCT2D(dims=image.shape)
        coeffs = FDCT @ image
        c_struct = FDCT.struct(coeffs)
        c_struct = CurveletDenoiser.get_fdct_struct(c_struct, coeff, thresholding)
        return (FDCT.H @ (FDCT.vect(c_struct))).real
    def get_ceoff_image(self, image, coeff):
        return None

