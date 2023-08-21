from matplotlib import pyplot as plt
import numpy as np
import curvelops as cl
import pywt
from skopt import gp_minimize, gbrt_minimize
from skopt.space import Integer, Real
from scipy.optimize import differential_evolution
import copy
import json

import sys
sys.path.append('/workspaces/python-image-processing')

from utils.image import *

def load_image(path):
    image = load_image_raw_file(path)
    image = convert_to_grayscale(image)
    image = alpha_correction_chain(tone_map(image))
    return image

ref_image = load_image('images/dice_caustics/output_0.raw')
x = load_image('images/dice_caustics/output_1.raw')

wavelet_name = 'sym2'
level = pywt.dwtn_max_level(x.shape, wavelet_name)
coeffs = pywt.wavedec2(x, wavelet_name, level=level)

t = [0] * (3 * len(coeffs) - 2)
#std = [0] * (3 * len(coeffs) - 2)
std = []
for i in range(1, len(coeffs)):
    for hvd in coeffs[i]:
        std.append(np.std(hvd))

# Define the search space
space = list(map(lambda x: Real(0, x), std))

count = 0
def objective_function(x):
    global count
    count += 1
    print(count, end='\r')
    coeffCopy = copy.deepcopy(coeffs)
    c = 0
    for i in range(1, len(coeffCopy)):
        a = []
        for img in coeffCopy[i]:
            m = np.mean(img)
            mask = np.logical_and(img >= m - x[c], img <= m + x[c])
            img[~mask] = m
            # a.append(pywt.threshold(img, x[c], mode='hard'))
            c += 1
        # coeffCopy[i] = (a[0], a[1], a[2])

    filtered_img = pywt.waverec2(coeffCopy, wavelet_name)
    local_mse = TrueMSE(filtered_img, ref_image)
    return local_mse

mse = TrueMSE(x, ref_image)
print(mse)

result = gp_minimize(objective_function, space)

print(result)