class DenoiserRunParamsString:
    def __init__(self, name, pairImage, metric, thresholding, search, iterations, denoiser):
        self.name = name
        self.pairImage = pairImage
        self.metric = metric
        self.thresholding = thresholding
        self.search = search
        self.iterations = iterations
        self.denoiser = denoiser

class DenoiserRunParams:
    def __init__(self, pairImage, metric, thresholding, searchMethod, iterations, denoiserMethod):
        self.pairImage = pairImage
        self.metric = metric
        self.thresholding = thresholding
        self.searchMethod = searchMethod
        self.iterations = iterations
        self.denoiserMethod = denoiserMethod

class Denoiser:
    def run(self, denoiserParams):
        return
    def get_image(self, image, coeff, thresholding):
        return
    def get_ceoff_image(self, image, coeff):
        return

