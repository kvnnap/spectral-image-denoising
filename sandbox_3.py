from utils.image import *
from evaluation.metric import *

from evaluation.fourier_denoiser import FourierDenoiser
from evaluation.thresholds import MultiplicationThreshold


ref_image = load_image('images/exp_1/povray_reflect_caustics_8.exr', False, False)
#noisy_image = load_image('images/exp_1/povray_reflect_caustics_2.exr', False, False)

denoiser = FourierDenoiser({})
mult = MultiplicationThreshold('mult')

(mag, phase) = denoiser.get_mag_phase(ref_image)
denoised_image = denoiser.get_image_ifft(ref_image.shape, mag, phase, mult, [1] * denoiser.coefficientLength)

score = local_mse(ref_image, denoised_image)

print(score)
