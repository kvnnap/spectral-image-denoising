from utils.string import extract_file_name
from utils.serialisation import to_string_obj

class DenoiserRunParamsString:
    def __init__(self, id, name, pairImage, imageLoader, metric, thresholding, search, iterations, denoiser, sample):
        self.id = id
        self.name = name
        self.pairImage = pairImage
        self.imageLoader = imageLoader
        self.metric = metric
        self.thresholding = thresholding
        self.search = search
        self.iterations = iterations
        self.denoiser = denoiser
        self.sample = sample
    
    def get_value(self, key):
        if key == 'ref-noisy':
            return f"{extract_file_name(self.pairImage[0])}-{extract_file_name(self.pairImage[1])}"
        elif key == 'denoiser':
            return self.denoiser['name'] if 'name' in self.denoiser else self.denoiser
        elif key == 'denoiser_coeff':
            return '/'.join([str(x) for x in self.denoiser.values()] if 'name' in self.denoiser else [self.denoiser])
        elif key in self.__dict__:
            return self.__dict__[key]
        else:
            return ''

