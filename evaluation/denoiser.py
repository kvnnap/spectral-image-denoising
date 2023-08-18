import numpy as np
import copy
import pywt
from image_utils import *
from skopt.space import Real

class DenoiserRunParamsString:
    def __init__(self, pairImage, metric, thresholding, search, coefficientLength, iterations, denoiser):
        self.pairImage = pairImage
        self.metric = metric
        self.thresholding = thresholding
        self.search = search
        self.coefficientLength = coefficientLength
        self.iterations = iterations
        self.denoiser = denoiser

class DenoiserRunParams:
    def __init__(self, pairImage, metric, thresholding, searchMethod, coefficientLength, iterations, denoiserMethod):
        self.pairImage = pairImage
        self.metric = metric
        self.thresholding = thresholding
        self.searchMethod = searchMethod
        self.coefficientLength = coefficientLength
        self.iterations = iterations
        self.denoiserMethod = denoiserMethod

class Denoiser:
    def run(self, denoiserParams):
        return
    def get_image(self, image, coeff, thresholding):
        return
    def get_ceoff_image(self, image, coeff):
        return
    
class FourierDenoiser(Denoiser):
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
    def get_image_ifft(image_shape, magnitude, phase_spectrum, treshold_fn, coeffs):
        mag = copy.deepcopy(magnitude)
        m = FourierDenoiser.create_multimask(image_shape, coeffs)
        mag = treshold_fn(mag, m)

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
        space = [Real(0, 1)] * denoiserParams.coefficientLength

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        (magnitude_spectrum, phase_spectrum) = FourierDenoiser.get_mag_phase(image)
        return FourierDenoiser.get_image_ifft(image.shape, magnitude_spectrum, phase_spectrum, thresholding, coeff)
    def get_ceoff_image(self, image, coeff):
        return FourierDenoiser.create_multimask(image.shape, coeff) * 255

class WaveletDenoiser(Denoiser):
    def __init__(self):
        self.wavelet_name = 'sym2'
        self.level = 0

    @staticmethod
    def filter_coeffs(coeffs, x, thresholding):
        c = 0
        for i in range(1, len(coeffs)):
            for img in coeffs[i]:
                tImg = thresholding(img, x[c])
                img[True] = tImg
                c += 1

    # need to parameterise wavelet_name, level, masking type (soft, hard)
    def run(self, denoiserParams):
        ref_image = load_image(denoiserParams.pairImage[0])
        image = load_image(denoiserParams.pairImage[1])

        level = pywt.dwtn_max_level(image.shape, self.wavelet_name) if (self.level == 0) else self.level
        coeffs = pywt.wavedec2(image, self.wavelet_name, level=level)

        std = []
        for i in range(1, len(coeffs)):
            for hvd in coeffs[i]: #hor,ver,diag
                std.append(np.std(hvd))

        # Define the search space
        space = list(map(lambda x: Real(0, x), std))

        def objective_function(x):
            coeffCopy = copy.deepcopy(coeffs)
            WaveletDenoiser.filter_coeffs(coeffCopy, x, denoiserParams.thresholding)
            filtered_img = pywt.waverec2(coeffCopy, self.wavelet_name)
            score = denoiserParams.metric(ref_image, filtered_img)
            return score

        result = denoiserParams.searchMethod(objective_function, space, denoiserParams.iterations)
        return result
    def get_image(self, image, coeff, thresholding):
        level = pywt.dwtn_max_level(image.shape, self.wavelet_name) if (self.level == 0) else self.level
        coeffs = pywt.wavedec2(image, self.wavelet_name, level=level)
        WaveletDenoiser.filter_coeffs(coeffs, coeff, thresholding)
        return pywt.waverec2(coeffs, self.wavelet_name)
    def get_ceoff_image(self, image, coeff):
        return None

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
