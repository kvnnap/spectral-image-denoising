class DenoiserRunParams:
    def __init__(self, pairImage, imageLoaderMethod, metric, thresholding, searchMethod, iterations, denoiserMethod):
        self.pairImage = pairImage
        self.imageLoaderMethod = imageLoaderMethod
        self.metric = metric
        self.thresholding = thresholding
        self.searchMethod = searchMethod
        self.iterations = iterations
        self.denoiserMethod = denoiserMethod

class Denoiser:
    def run(self, denoiserParams, dpString):
        return None
    def get_image(self, image, coeff, thresholding):
        return None
    def get_ceoff_image(self, image, coeff, thresholding):
        return None

