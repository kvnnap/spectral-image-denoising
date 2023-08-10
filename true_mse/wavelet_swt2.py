import numpy as np
import pywt
from matplotlib import pyplot as plt
from skopt.space import Integer, Real
from skopt import gp_minimize, gbrt_minimize
from skimage.metrics import structural_similarity as ssim
import copy
# import warnings
# warnings.simplefilter('error')

import sys
sys.path.append('/workspaces/python-image-processing')

from image_utils import *

new_shape = (1024, 1024)

def comparison_fn(input, ref):
    #return TrueMSE(input, ref)
    return 1.0 - ssim(ref, input, data_range=input.max() - input.min())

ref_image = load_image('images/dice_caustics/output_0.raw')
orig_shape = ref_image.shape
ref_image = crop_enlarge(ref_image, new_shape)
ref_image = crop_enlarge(ref_image, orig_shape)

image = load_image('images/dice_caustics/output_1.raw')
image = crop_enlarge(image, new_shape)
image = crop_enlarge(image, orig_shape)

orig_mse = comparison_fn(image, ref_image)
image = crop_enlarge(image, new_shape)

wavelet_name = 'sym2'
level = pywt.swt_max_level(max(image.shape))
level = 6
coeffs = pywt.swt2(image, wavelet_name, level)

std = []
for c in coeffs:
    for hvd in c[1]:
        std.append(np.std(hvd))

# Define the search space
space = list(map(lambda x: Real(0.01, 1), std))
m = 'garrote'

def get_coeffs(origCoeffs, x):
    coeffCopy = copy.deepcopy(origCoeffs)
    c = 0
    for cof in coeffCopy:
        # a = []
        for img in cof[1]:
            # m = np.mean(img)
            # mask = np.logical_and(img >= m - x[c], img <= m + x[c])
            # img[~mask] = m
            img[True] = pywt.threshold(img, x[c], m)
            # a.append(pywt.threshold(img, x[c], mode='hard'))
            c += 1
        # coeffCopy[i] = (a[0], a[1], a[2])
    return coeffCopy

count = 0
def objective_function(x):
    global count
    count += 1
    print(count, end='\r')
    coeffCopy = get_coeffs(coeffs, x)

    filtered_img = pywt.iswt2(coeffCopy, wavelet_name)
    filtered_img = crop_enlarge(filtered_img, orig_shape)
    score = comparison_fn(filtered_img, ref_image)
    return score


result = gp_minimize(objective_function, space, n_calls=200)

final_img = crop_enlarge(pywt.iswt2(get_coeffs(coeffs, result.x), wavelet_name), orig_shape)
image = crop_enlarge(image, orig_shape)

ax = plt.subplot(221)
plt.subplot(222, sharex=ax, sharey=ax)

plt.subplot(221), plt.imshow(image, cmap='gray')
plt.title(f'Original Image: MSE {orig_mse:.2f}'), plt.xticks([]), plt.yticks([])
plt.subplot(222), plt.imshow(final_img, cmap='gray')
plt.title(f'Filtered Image: MSE {result.fun:.2f}'), plt.xticks([]), plt.yticks([])
plt.subplot(223), plt.plot(result.func_vals)
plt.title('Progression'), plt.xticks([]), plt.yticks([])
# plt.subplot(224), plt.imshow(freq_coeffs, cmap='gray')
# plt.title('Applied filter'), plt.xticks([]), plt.yticks([])
plt.show()

# for c in coeffs:
#     # if (len(c) != 3):
#     #     plt.imshow(c, cmap='gray')
#     #     plt.show()
#     #     continue
#     a = c[0]
#     (h, v, d) = c[1]
#     h[True] = pywt.threshold(h, t, m)
#     v[True] = pywt.threshold(v, t, m)
#     d[True] = pywt.threshold(d, t, m)
#     # h[300:, :200] *= 0.1
#     # v[300:, :200] *= 0.1
#     # d[300:, :200] *= 0.1
    
#     # plt.subplot(221), plt.imshow(a, cmap='gray')
#     # plt.title(f'A'), plt.xticks([]), plt.yticks([])
#     # plt.subplot(222), plt.imshow(h, cmap='gray')
#     # plt.title(f'H'), plt.xticks([]), plt.yticks([])
#     # plt.subplot(223), plt.imshow(v, cmap='gray')
#     # plt.title('V'), plt.xticks([]), plt.yticks([])
#     # plt.subplot(224), plt.imshow(d, cmap='gray')
#     # plt.title('D'), plt.xticks([]), plt.yticks([])
#     # plt.show()
