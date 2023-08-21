from matplotlib import pyplot as plt
import numpy as np
import curvelops as cl
import pywt
from skopt import gp_minimize, gbrt_minimize
from skopt.space import Integer, Real
from scipy.optimize import differential_evolution
import copy
import json

import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable

from curvelops.plot import (
    create_inset_axes_grid,
    create_axes_grid,
    overlay_disks,
)

from utils.image import *

def load_image(path):
    image = load_image_raw_file(path)
    image = convert_to_grayscale(image)
    image = alpha_correction_chain(tone_map(image))
    return image

ref_image = load_image('images/dice_caustics/output_0.raw')
image = load_image('images/dice_caustics/output_1.raw')
image = ref_image
image = image.T
FDCT = cl.FDCT2D(dims=image.shape, nbscales=4, allcurvelets=False)
c_other = FDCT @ image
c_struct = FDCT.struct(c_other)

print(np.sum(image.astype(np.float64) ** 2))
print(np.sum((FDCT.H @ (FDCT.vect(c_struct))).real.astype(np.float64) ** 2))

# In our previous example, we considered a "wedge" to be symmetric with respect
# to the origin. The `FDCT2D` does not do this by default. Moreover, it will always
# output each unsymmetrized wedge separately. In this example, `nbangles_coarse = 8`
# really only gives us 4 independent wedges. We will symmetrize them as follows
# KEVIN NOTES: For real inputs, if c_struct[iscale][iwedge] = a+bi, then 
# c_struct[iscale][iwedge + nbangles // 2] = a - bi

# for iscale in range(len(c_struct)):
#     if len(c_struct[iscale]) == 1:  # Not a curvelet transform
#         #print(f"Wedges in scale {iscale+1}: {len(c_struct[iscale])}")
#         continue
#     nbangles = len(c_struct[iscale])
#     for iwedge in range(nbangles // 2):
#         c_struct[iscale][iwedge] = (
#             2 * c_struct[iscale][iwedge]  # Wedge
#             #+ c_struct[iscale][iwedge + nbangles // 2]  # Symmetric counterpart
#         ) #/ np.sqrt(2) # not sure about the square root since we're zeroing instead of truncating
#         #c_struct[iscale][iwedge] = np.zeros_like(c_struct[iscale][iwedge])
#         c_struct[iscale][iwedge + nbangles // 2] = np.zeros_like(c_struct[iscale][iwedge + nbangles // 2])
#     #c_struct[iscale] = c_struct[iscale][: nbangles // 2]
#     #print(f"Wedges in scale {iscale+1}: {len(c_struct[iscale])}")
# zo = (FDCT.H @ (FDCT.vect(c_struct))).real
# print(np.sum(zo.astype(np.float64) ** 2))

# plt.imshow(zo.T, cmap='gray')
# plt.show()

# inputfile = "sigmoid.npz"
# d = np.load(inputfile)
# image = d["sigmoid"]
# FDCT = cl.FDCT2D(dims=image.shape, nbscales=4, nbangles_coarse=8, allcurvelets=False)
# c_struct = FDCT.struct(FDCT @ image)


nx, nz = image.shape
rows, cols = 4, 7
fig, ax = plt.subplots()
ax.imshow(
    image.T, cmap="gray"
)
axesin = create_inset_axes_grid(
    ax, rows, cols, width=0.4, kwargs_inset_axes=dict(projection="polar")
)
overlay_disks(c_struct, axesin, linewidth=0.0, cmap="turbo")

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
mpl.colorbar.ColorbarBase(
    cax, cmap="turbo", norm=mpl.colors.Normalize(vmin=0, vmax=1)
)

# fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=True)
# plt.colorbar(axes[0].imshow(x, cmap='gray'))
# # plt.colorbar(axes[1].imshow(y, cmap='gray'))
# # plt.colorbar(axes[2].imshow(z, cmap='gray'))
plt.show()

