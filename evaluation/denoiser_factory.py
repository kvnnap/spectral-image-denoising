from fourier_denoiser import FourierDenoiser
from wavelet_denoiser import WaveletDenoiser
from wavelet_swt_denoiser import WaveletSwtDenoiser
from curvelet_denoiser import CurveletDenoiser

class DenoiserFactory:
    @staticmethod
    def create(denoiserName):
        name = denoiserName.strip().lower()
        if (name == "fourier"):
            return FourierDenoiser()
        elif (name == "wavelet"):
            return WaveletDenoiser()
        elif (name == "wavelet_swt"):
            return WaveletSwtDenoiser()
        elif (name == "curvelet"):
            return CurveletDenoiser()
        else:
            raise ValueError(f"Invalid denoiser name {denoiserName}")
