from functools import lru_cache
from evaluation.denoiser_factory import DenoiserFactory
from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import MetricFactory
from evaluation.thresholds import ThresholdFactory

class ResultImageProcessor():
    def __init__(self, run):
        dp = run.denoiserParams
        self.run = run
        self.imageLoaderMethod = ImageLoaderFactory.create(dp.imageLoader)
        self.thresholdMethod = ThresholdFactory.create(dp.thresholding)
        self.denoiserMethod = DenoiserFactory.create(dp.denoiser)
        self.metricMethod = MetricFactory.create(dp.metric)
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
        (image, reconstructedImage, _) = self.get(False, coeffId)
        return self.metricMethod(image, reconstructedImage)
    
    def update_image_path(self, path):
        self.image = self.imageLoaderMethod(path)
        self.get.cache_clear()

    def get_image(self, path):
        return self.imageLoaderMethod(path)
