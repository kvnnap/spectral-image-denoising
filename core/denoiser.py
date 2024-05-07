import copy

from utils.array import hash_floats
from utils.string import extract_file_name

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
    
    @staticmethod
    def obj_config_to_str(objConfig):
        return '/'.join([ objConfig['name'],  *[str(v) for k, v in objConfig.items() if k != 'name']] if 'name' in objConfig else [objConfig])

    def get_value(self, key):
        if key == 'ref-noisy':
            return f"{extract_file_name(self.pairImage[0])}-{extract_file_name(self.pairImage[1])}"
        elif key == 'denoiser':
            return self.denoiser['name'] if 'name' in self.denoiser else self.denoiser
        elif key == 'denoiser_coeff':
            return DenoiserRunParamsString.obj_config_to_str(self.denoiser)
        elif key == 'search':
            search = copy.deepcopy(self.search)
            if 'x' in search:
                search['x'] = hash_floats(search['x'])[:8]
            return DenoiserRunParamsString.obj_config_to_str(search)
        elif key == 'sample':
            return self.sample if 'sample' in self.__dict__ else 0
        elif key in self.__dict__:
            return self.__dict__[key]
        else:
            return ''
        
    def compare(self, other):
        return all(self.get_value(x) == other.get_value(x) for x in self.__dict__.keys())


