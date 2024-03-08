from evaluation.fourier_denoiser import FourierDenoiser
from evaluation.wavelet_denoiser import WaveletDenoiser
from evaluation.wavelet_swt_denoiser import WaveletSwtDenoiser
from evaluation.curvelet_denoiser import CurveletDenoiser

class DenoiserFactory:
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
