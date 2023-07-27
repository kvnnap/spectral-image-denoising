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

from image_utils import *

def load_image(path):
    image = load_image_raw_file(path)
    image = convert_to_grayscale(image)
    image = alpha_correction_chain(tone_map(image))
    return image

ref_image = load_image('images/dice_caustics/output_0.raw')
x = load_image('images/dice_caustics/output_1.raw')

mse = TrueMSE(x, ref_image)
print(mse)

FDCT = cl.FDCT2D(dims=x.shape)
c = FDCT @ x
c_struct = FDCT.struct(c)

#
std = []
for i, s in enumerate(c_struct):
    std.append(5)

count = 0

def get_fdct_struct(c_str, x):
    c_copy = copy.deepcopy(c_str)
    for i, s in enumerate(c_copy):
        for j, w in enumerate(s):
            c_copy[i][j] = pywt.threshold(c_copy[i][j], x[i], mode='soft')
    return c_copy

def objective_function(x):
    global count
    count += 1
    print(count, end='\r')
    c_copy = get_fdct_struct(c_struct, x)
    local_mse = TrueMSE((FDCT.H @ (FDCT.vect(c_copy))).real, ref_image)
    return local_mse

def naive_min(c_str):
    global count
    ts = []
    #c_filt = np.empty(len(c_struct), dtype=object)
    c_copy = copy.deepcopy(c_str)
    for i, c_scale in enumerate(c_copy):
        count += 1
        print(count, end='\r')
        scale_std = std[i]

        orig = c_scale.copy()
        min_scale = c_scale.copy()
        mse = np.inf
        t = 0
        for delta in np.arange(0, 1, 0.1):
            t = delta * scale_std

            # Threshold the wedge
            for j, w in enumerate(c_scale):
                c_copy[i][j] = pywt.threshold(c_copy[i][j], t, mode='soft')
            # for k, inner in enumerate(wedge):
            #     c_str[i][j][k] = pywt.threshold(inner, t, mode='soft')
            x_mse = TrueMSE((FDCT.H @ (FDCT.vect(c_copy))).real, ref_image)
            if (x_mse >= mse):
                break
            min_scale = c_copy[i].copy()
            mse = x_mse
            c_copy[i] = orig.copy()
        ts.append(t)
        c_copy[i] = min_scale.copy()

    return ts

# Define the search space
space = list(map(lambda x: Real(0, x), std))
result = gp_minimize(objective_function, space, n_calls=250)
# with open("y_c", "w") as fp:
#     json.dump(result.x, fp)
c_struct_1 = get_fdct_struct(c_struct, result.x)
y = (FDCT.H @ (FDCT.vect(c_struct_1))).real


# space = list(map(lambda x: (0, x[2]), wedgeMap))
# result = differential_evolution(objective_function, space)

#y=x

count = 0
coeffs = naive_min(c_struct)
# with open("z_c", "w") as fp:
#     json.dump(coeffs, fp)
# with open("z_c2", "r") as fp:
#     coeffs = json.load(fp)
c_struct_2 = get_fdct_struct(c_struct, coeffs)
zo = (FDCT.H @ (FDCT.vect(c_struct_2))).real
#z = zo - zo.min()
z = np.maximum(zo, 0)

mse = TrueMSE(y, ref_image)
print(mse)
mse = TrueMSE(z, ref_image)
print(mse)

print(count)

# x = alpha_correction_chain(tone_map(x))
# y = alpha_correction_chain(tone_map(y))
# z = alpha_correction_chain(tone_map(z))

fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=True)
plt.colorbar(axes[0].imshow(x, cmap='gray'))
plt.colorbar(axes[1].imshow(y, cmap='gray'))
plt.colorbar(axes[2].imshow(z, cmap='gray'))
plt.show()

