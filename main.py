import pywt
import numpy as np
import matplotlib.pyplot as plt

# Load input image as grayscale
img = plt.imread('images/dice_2.png')
if img.ndim == 3:
    img = np.mean(img, axis=2)

# Perform 2D wavelet transform using PyWavelets
coeffs = pywt.dwt2(img, 'haar')

# Separate the coefficients into approximation (low-pass) and detail (high-pass) components
LL, (LH, HL, HH) = coeffs

# Visualize the transformed image
plt.figure(figsize=(8,8))
plt.subplot(2,2,1), plt.imshow(LL, cmap='gray'), plt.title('Approximation (LL)')
plt.subplot(2,2,2), plt.imshow(LH, cmap='gray'), plt.title('Horizontal detail (LH)')
plt.subplot(2,2,3), plt.imshow(HL, cmap='gray'), plt.title('Vertical detail (HL)')
plt.subplot(2,2,4), plt.imshow(HH, cmap='gray'), plt.title('Diagonal detail (HH)')
plt.show()
