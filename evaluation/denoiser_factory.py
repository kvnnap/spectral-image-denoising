from wavelet_denoiser import WaveletDenoiser
from fourier_denoiser import FourierDenoiser

class DenoiserFactory:
    @staticmethod
    def create(denoiserName):
        name = denoiserName.strip().lower()
        if (name == "fourier"):
            return FourierDenoiser()
        elif (name == "wavelet"):
            return WaveletDenoiser()
        else:
            raise ValueError(f"Invalid denoiser name {denoiserName}")
