from fourier_denoiser import FourierDenoiser
from wavelet_denoiser import WaveletDenoiser
from wavelet_swt_denoiser import WaveletSwtDenoiser
from curvelet_denoiser import CurveletDenoiser
import itertools

class DenoiserFactory:
    @staticmethod
    def unpack_config(denoiser):
        denoiserConfig = {}

        if ('name' in denoiser):
            denoiserConfig = denoiser
        else:
            denoiserConfig['name'] = denoiser

        name = denoiserConfig.pop('name').strip().lower()
        
        keys = denoiserConfig.keys()
        values = denoiserConfig.values()
        combinations = list(itertools.product(*values))
        configs = [{key: value for key, value in zip(keys, combination)} for combination in combinations]
        for config in configs:
            config['name'] = name
        return configs

    @staticmethod
    def create(denoiserConfig):
        clsMap = {
            "fourier": FourierDenoiser,
            "wavelet": WaveletDenoiser,
            "wavelet_swt": WaveletSwtDenoiser,
            "curvelet": CurveletDenoiser,
        }
        name = denoiserConfig['name']
        if name not in clsMap:
            raise ValueError(f"Invalid denoiser name {name}")
        return clsMap[name](denoiserConfig)
