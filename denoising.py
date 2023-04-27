import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pywt
import cv2

wavelet_name = 'haar'

# Load image
img = Image.open('images/dice_2.png')

# Convert to grayscale
img_gray = img.convert('L')

img_gray = np.array(img_gray)

level = pywt.dwtn_max_level(img_gray.shape, wavelet_name)
level = 2

# Decompose image using wavedec2
coeffs = pywt.wavedec2(img_gray, wavelet_name, level=level)

# filter stuff
threshold = 10
mode = 'hard'
sigma = 0.45
for i in range(1, len(coeffs)):
    (h,v,d) = coeffs[i]
    for img in [h, v, d]:
        s = np.std(img)
        m = np.mean(img)
        mask = np.logical_and(img >= m - sigma * s, img <= m + sigma * s)
        img[~mask] = m
    
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
plt.imshow(arr, cmap=plt.cm.gray)
plt.show()


fig, axes = plt.subplots(nrows=2)
axes[0].imshow(img_gray, cmap=plt.cm.gray)
axes[1].imshow(img_result, cmap=plt.cm.gray)

plt.show()

# # Show all coefficients
# for i in range(len(coeffs)):
#     plt.imshow(coeffs[i], cmap='gray')