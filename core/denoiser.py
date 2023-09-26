class DenoiserRunParamsString:
    def __init__(self, id, name, pairImage, imageLoader, metric, thresholding, search, iterations, denoiser):
        self.id = id
        self.name = name
        self.pairImage = pairImage
        self.imageLoader = imageLoader
        self.metric = metric
        self.thresholding = thresholding
        self.search = search
        self.iterations = iterations
        self.denoiser = denoiser
