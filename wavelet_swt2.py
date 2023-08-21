import numpy as np
import pywt
from matplotlib import pyplot as plt
from pywt._doc_utils import wavedec2_keys, draw_2d_wp_basis

from utils.image import *

x = load_image('images/dice_caustics/output_1.raw')
orig_shape = x.shape
#x = resize_to_nearest_power_of_2_square(x)
x = crop_enlarge(x, (1024, 1024))

wavelet_name = 'sym2'
level = pywt.swt_max_level(max(x.shape))
level = 6
coeffs = pywt.swt2(x, wavelet_name, level)

print('hello')

t = 0.75
m = 'soft'

for c in coeffs:
    # if (len(c) != 3):
    #     plt.imshow(c, cmap='gray')
    #     plt.show()
    #     continue
    a = c[0]
    (h, v, d) = c[1]
    h[True] = pywt.threshold(h, t, m)
    v[True] = pywt.threshold(v, t, m)
    d[True] = pywt.threshold(d, t, m)
    # h[300:, :200] *= 0.1
    # v[300:, :200] *= 0.1
    # d[300:, :200] *= 0.1
    
    # plt.subplot(221), plt.imshow(a, cmap='gray')
    # plt.title(f'A'), plt.xticks([]), plt.yticks([])
    # plt.subplot(222), plt.imshow(h, cmap='gray')
    # plt.title(f'H'), plt.xticks([]), plt.yticks([])
    # plt.subplot(223), plt.imshow(v, cmap='gray')
    # plt.title('V'), plt.xticks([]), plt.yticks([])
    # plt.subplot(224), plt.imshow(d, cmap='gray')
    # plt.title('D'), plt.xticks([]), plt.yticks([])
    # plt.show()

res = pywt.iswt2(coeffs, wavelet_name)
res = crop_enlarge(res, orig_shape)
plt.imshow(res, cmap='gray')
plt.show()