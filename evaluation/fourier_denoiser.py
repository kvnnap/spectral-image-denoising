import numpy as np
import copy
from utils.image import *
from skopt.space import Real
from denoiser import Denoiser

class FourierDenoiser(Denoiser):
    def __init__(self, config):
        super().__init__()
        self.coefficientLength = config['coefficientLength'] if 'coefficientLength' in config else 16

    # Function to create elliptical masks for multiple frequencies
    @staticmethod
    def create_multimask(image_shape, attenuations):
        rows, cols = image_shape
        center_row, center_col = rows // 2, cols // 2

        y, x = np.ogrid[:rows, :cols]
        z = np.sqrt((x - center_col) ** 2 + ((y - center_row) * (cols / rows)) ** 2)

        mask = np.ones(image_shape, dtype=np.float32)
        # step_size = center_col / len(attenuations)
        step_size = z.max() / len(attenuations)
        for i, att in enumerate(attenuations):
            rng = (step_size * i <= z) & (z < step_size * (i + 1))
            mask[rng] = att
        return mask

    # Fourier methods
    @staticmethod
    def get_image_ifft(image_shape, magnitude, phase_spectrum, thresholding, coeffs):
        mag = copy.deepcopy(magnitude)
        m = FourierDenoiser.create_multimask(image_shape, coeffs)
        mag = thresholding.fn(mag, m)

        reconstructed_fft_image = mag * np.exp(1j * phase_spectrum)
        reconstructed_fft_image = np.fft.ifftshift(reconstructed_fft_image)
        return np.fft.ifft2(reconstructed_fft_image).real
    
    @staticmethod
    def get_mag_phase(image):
        # Step 2: Perform the real-to-complex Fourier transform - since input is real
        fft_image = np.fft.fft2(image)

        # Step 3: Shift zero-frequency components to the center
        fft_shifted = np.fft.fftshift(fft_image)

        # Get mag and phase
        magnitude_spectrum = np.abs(fft_shifted)
        phase_spectrum = np.angle(fft_shifted)
        return (magnitude_spectrum, phase_spectrum)

    def run(self, denoiserParams):
        ref_image = load_image(denoiserParams.pairImage[0])
        image = load_image(denoiserParams.pairImage[1])

        (magnitude_spectrum, phase_spectrum) = FourierDenoiser.get_mag_phase(image)

        def objective_function(x):
            reconstructed_image = FourierDenoiser.get_image_ifft(image.shape, magnitude_spectrum, phase_spectrum, denoiserParams.thresholding, x)
            score = denoiserParams.metric(ref_image, reconstructed_image)
            return score
        
        # build space
        space = denoiserParams.thresholding.get_space([1] * self.coefficientLength)

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        (magnitude_spectrum, phase_spectrum) = FourierDenoiser.get_mag_phase(image)
        return FourierDenoiser.get_image_ifft(image.shape, magnitude_spectrum, phase_spectrum, thresholding, coeff)
    def get_ceoff_image(self, image, coeff):
        return FourierDenoiser.create_multimask(image.shape, coeff) * 255
