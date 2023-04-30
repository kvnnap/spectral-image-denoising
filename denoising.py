import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pywt
import cv2
from scipy import ndimage
from image_utils import *


def filter_std_dev(coeff, sigma):
    (h,v,d) = coeff
    for img in [h, v, d]:
        s = np.std(img)
        m = np.mean(img)
        mask = np.logical_and(img >= m - sigma * s, img <= m + sigma * s)
        img[~mask] = m

def filter_median(coeff, size):
    (h,v,d) = coeff
    for img in [h, v ,d]:
        temp = ndimage.median_filter(img, size=size)
        mask = np.logical_and(True, True)
        img[mask] = temp

wavelet_name = 'sym2'

# Load image
img = load_image_raw_file('images/dice_2.raw')
img_gray = convert_to_grayscale(img)

# Convert to grayscale

level = pywt.dwtn_max_level(img_gray.shape, wavelet_name)
#level = 2

# Decompose image using wavedec2
coeffs = pywt.wavedec2(img_gray, wavelet_name, level=level)

# filter stuff
threshold = 1
mode = 'hard'
sigma = 0.45
# for i in range(1, 4):
#     filter_std_dev(coeffs[i], sigma)
for i in range(1, len(coeffs)):
    # if i == 1:
    #     continue
    filter_std_dev(coeffs[i], 2)
    #filter_median(coeffs[i], 3)
    (h,v,d) = coeffs[i]
    # fig, axes = plt.subplots(3)
    # plt.colorbar(axes[0].imshow((h - np.mean(h)) / np.std(h), cmap='hot'))
    # plt.colorbar(axes[1].imshow((v - np.mean(v)) / np.std(v), cmap='hot'))
    # plt.colorbar(axes[2].imshow((d - np.mean(d)) / np.std(d), cmap='hot'))
    # plt.show()
    # h = np.zeros_like(h)
    # v = np.zeros_like(v)
    # d = np.zeros_like(d)
    # h = pywt.threshold(h, threshold, mode=mode)
    # v = pywt.threshold(v, threshold, mode=mode)
    # d = pywt.threshold(d, threshold, mode=mode)
    # h = cv2.Canny(np.uint8(h), 100, 200)
    # v = cv2.Canny(np.uint8(v), 100, 200)
    # d = cv2.Canny(np.uint8(d), 100, 200)
    # coeffs[i] = (h,v,d)

# perform inverse
img_result = pywt.waverec2(coeffs, wavelet_name)

# normalize each coefficient array independently for better visibility
viewingCoeffs = [None] * len(coeffs)
viewingCoeffs[0] = coeffs[0]
viewingCoeffs[0] /= np.abs(coeffs[0]).max()
for detail_level in range(level):
    viewingCoeffs[detail_level + 1] = [d/np.abs(d).max() for d in coeffs[detail_level + 1]]

# print
arr, slices = pywt.coeffs_to_array(viewingCoeffs)
plt.colorbar(plt.imshow(arr, cmap=plt.cm.gray))
plt.show()

img_gray = alpha_correction_chain(tone_map(img_gray))
img_result = alpha_correction_chain(tone_map(img_result))
#img_result = img_result / np.abs(img_result).max()

fig, axes = plt.subplots(nrows=2)
plt.colorbar(axes[0].imshow(img_gray, cmap=plt.cm.gray))
plt.colorbar(axes[1].imshow(np.abs(img_result), cmap=plt.cm.gray))

plt.show()

# # Show all coefficients
# for i in range(len(coeffs)):
#     plt.imshow(coeffs[i], cmap='gray')