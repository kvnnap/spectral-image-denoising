from functools import lru_cache
from evaluation.denoiser_factory import DenoiserFactory
from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import MetricFactory
from evaluation.thresholds import ThresholdFactory
from evaluation.metric import *

class ResultImageProcessor():
    def __init__(self, run):
        dp = run.denoiserParams
        self.denoiserParams = run.denoiserParams
        self.run = run
        self.imageLoaderMethod = ImageLoaderFactory.create(dp.imageLoader)
        self.thresholdMethod = ThresholdFactory.create(dp.thresholding)
        self.denoiserMethod = DenoiserFactory.create(dp.denoiser)
        self.metricMethod = MetricFactory.create(dp.metric)
        self.refImage = self.imageLoaderMethod(dp.pairImage[0])
        self.image = self.imageLoaderMethod(dp.pairImage[1])
    
    @lru_cache
    def get(self, renderCoeffImage = True, coeffId = None):
        coeffs = self.run.denoiserResult.x if coeffId is None else self.run.denoiserResult.x_iters[coeffId]
        den = self.denoiserMethod.get_image(self.image, coeffs, self.thresholdMethod)
        den_coeff = None
        if (renderCoeffImage):
            den_coeff = self.denoiserMethod.get_ceoff_image(self.image, coeffs, self.thresholdMethod)
        return (self.image, den, den_coeff)
    
    def compute_score(self, coeffId = None):
        (_, reconstructedImage, _) = self.get(False, coeffId)
        ret_obj = {
            'mse': (local_mse(self.refImage, self.image, self.denoiserParams), local_mse(self.refImage, reconstructedImage, self.denoiserParams)),
            'ssim': (local_ssim(self.refImage, self.image, self.denoiserParams), local_ssim(self.refImage, reconstructedImage, self.denoiserParams)),
            'psnr': (local_psnr(self.refImage, self.image, self.denoiserParams), local_psnr(self.refImage, reconstructedImage, self.denoiserParams)),
            'hdrvdp3': (local_hdrvdp3(self.refImage, self.image, self.denoiserParams), local_hdrvdp3(self.refImage, reconstructedImage, self.denoiserParams))
        }
        return ret_obj
    
    def update_image_path(self, path):
        self.update_image(self.imageLoaderMethod(path))

    def update_ref_image_path(self, path):
        self.update_ref_image(self.imageLoaderMethod(path))

    def update_image(self, image):
        self.image = image
        self.get.cache_clear()

    def update_ref_image(self, refImage):
        self.refImage = refImage

    def get_image(self, path):
        return self.imageLoaderMethod(path)
