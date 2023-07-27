import copy
from skopt import gp_minimize
from skopt.space import Integer, Real
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('/workspaces/python-image-processing')
from image_utils import *

def load_image(path):
    image = load_image_raw_file(path)
    image = convert_to_grayscale(image)
    image = alpha_correction_chain(tone_map(image))
    return image

# Function to create elliptical masks for multiple frequencies
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


# Step 1: Read the image using OpenCV
ref_image = load_image('images/dice_caustics/output_0.raw')
image = load_image('images/dice_caustics/output_1.raw')

# Step 2: Perform the real-to-complex Fourier transform - since input is real
fft_image = np.fft.fft2(image)

# Step 3: Shift zero-frequency components to the center
fft_shifted = np.fft.fftshift(fft_image)

# Get mag and phase
magnitude_spectrum = np.abs(fft_shifted)
phase_spectrum = np.angle(fft_shifted)


def get_image(image_shape, magnitude, phase_spectrum, coeffs):
    mag = copy.deepcopy(magnitude)
    m = create_multimask(image_shape, coeffs)
    mag *= m

    reconstructed_fft_image = mag * np.exp(1j * phase_spectrum)
    reconstructed_fft_image = np.fft.ifftshift(reconstructed_fft_image)
    return np.fft.ifft2(reconstructed_fft_image).real

count = 0
def objective_function(x):
    global count
    count += 1
    print(count, end='\r')
    reconstructed_image = get_image(image.shape, magnitude_spectrum, phase_spectrum, x)
    local_mse = TrueMSE(reconstructed_image, ref_image)
    return local_mse

# Define the search space
space = [Real(0, 1)] * 32

mse = TrueMSE(image, ref_image)

result = gp_minimize(objective_function, space, n_calls=250)

final_image = get_image(image.shape, magnitude_spectrum, phase_spectrum, result.x)
freq_coeffs = create_multimask(image.shape, result.x) * 255

#magnitude_spectrum = 20 * np.log(magnitude_spectrum)

# Step 5: Display the original and Fourier transformed images
# white_image = np.ones(image.shape, dtype=np.float32) * 255
# white_image *= m
# plt.imshow(white_image, cmap='gray')
# plt.show()

plt.subplot(221), plt.imshow(image, cmap='gray')
plt.title(f'Original Image: MSE {mse:.2f}'), plt.xticks([]), plt.yticks([])
plt.subplot(222), plt.imshow(final_image, cmap='gray')
plt.title(f'Filtered Image: MSE {result.fun:.2f}'), plt.xticks([]), plt.yticks([])
plt.subplot(223), plt.plot(result.func_vals)
plt.title('Progression'), plt.xticks([]), plt.yticks([])
plt.subplot(224), plt.imshow(freq_coeffs, cmap='gray')
plt.title('Applied filter'), plt.xticks([]), plt.yticks([])
plt.show()

