import numpy as np
import copy
from evaluation.denoiser import Denoiser
from utils.image import seperate_channels, merge_channels
from utils.math import get_threshold_max

class FourierDenoiser(Denoiser):
    def __init__(self, config):
        super().__init__()
        self.coefficientLength = config['coefficientLength'] if 'coefficientLength' in config else 16

    @staticmethod
    def get_multimask_ranges(image_shape, attenuations_size):
        rows, cols, *_ = image_shape
        center_row, center_col = rows // 2, cols // 2

        y, x = np.ogrid[:rows, :cols]
        z = np.sqrt((x - center_col) ** 2 + ((y - center_row) * (cols / rows)) ** 2)

        # step_size = center_col / attenuations_size
        step_size = z.max() / attenuations_size
        ranges_list = []
        for i in range(attenuations_size):
            if i == attenuations_size - 1:
                rng = step_size * i <= z
            else:
                rng = (step_size * i <= z) & (z < step_size * (i + 1))
            ranges_list.append(rng)
        return ranges_list

    # Function to create elliptical masks for multiple frequencies
    @staticmethod
    def create_multimask(image_shape, attenuations):
        ranges_list = FourierDenoiser.get_multimask_ranges(image_shape, len(attenuations))
        mask = np.ones(image_shape, dtype=np.float32)
        for i, rng in enumerate(ranges_list):
            mask[rng] = attenuations[i]
        return mask

    # Fourier methods
    @staticmethod
    def get_image_ifft(image_shape, magnitude, phase_spectrum, thresholding, coeffs):
        mag = copy.deepcopy(magnitude)
        m = FourierDenoiser.create_multimask(image_shape, coeffs)
        mag = thresholding.fn(mag, m)

        reconstructed_fft_image = mag * np.exp(1j * phase_spectrum)
        reconstructed_fft_image = np.transpose(reconstructed_fft_image, (2, 0, 1))
        reconstructed_fft_image = list(map(lambda x: np.clip(np.fft.ifft2(np.fft.ifftshift(x)).real, 0, None), reconstructed_fft_image))
        return merge_channels(reconstructed_fft_image)
    
    @staticmethod
    def get_mag_phase(image):
        retList = []
        for im in seperate_channels(image):
            # Step 2: Perform the real-to-complex Fourier transform - since input is real
            fft_image = np.fft.fft2(im)

            # Step 3: Shift zero-frequency components to the center
            fft_shifted = np.fft.fftshift(fft_image)

            # Get mag and phase
            magnitude_spectrum = np.abs(fft_shifted)
            phase_spectrum = np.angle(fft_shifted)
            retList.append((magnitude_spectrum, phase_spectrum))
        return tuple([np.stack(list(x), axis=-1) for x in zip(*retList)])

    def run(self, denoiserParams, dpString):
        ref_image = denoiserParams.imageLoaderMethod(denoiserParams.pairImage[0])
        image = denoiserParams.imageLoaderMethod(denoiserParams.pairImage[1])

        (magnitude_spectrum, phase_spectrum) = FourierDenoiser.get_mag_phase(image)

        def objective_function(x):
            reconstructed_image = FourierDenoiser.get_image_ifft(image.shape, magnitude_spectrum, phase_spectrum, denoiserParams.thresholding, x)
            score = denoiserParams.metric(ref_image, reconstructed_image, dpString)
            return score
        
        # build space
        mask_ranges = FourierDenoiser.get_multimask_ranges(image.shape, self.coefficientLength)
        measure = [get_threshold_max(magnitude_spectrum[rng]) for rng in mask_ranges]
        # measure = [1] * self.coefficientLength
        space = denoiserParams.thresholding.get_space(measure)

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        (magnitude_spectrum, phase_spectrum) = FourierDenoiser.get_mag_phase(image)
        return FourierDenoiser.get_image_ifft(image.shape, magnitude_spectrum, phase_spectrum, thresholding, coeff)
    def get_ceoff_image(self, image, coeff, thresholding):
        return FourierDenoiser.create_multimask(image.shape, coeff)
