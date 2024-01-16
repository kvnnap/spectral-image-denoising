from matplotlib import pyplot as plt
import numpy as np
import curvelops as cl
import pywt
from skopt import gp_minimize, gbrt_minimize
from skopt.space import Integer, Real
from scipy.optimize import differential_evolution
import copy
import json

from utils.image import *

def load_image(path):
    image = load_image_raw_file(path)
    image = convert_to_grayscale(image)
    image = alpha_correction_chain(tone_map(image))
    return image

ref_image = load_image('images/dice_caustics/output_0.raw')[:, :, 0]
image = load_image('images/dice_caustics/output_1.raw')[:, :, 0]

FDCT = cl.FDCT2D(dims=image.shape, nbscales=3)
c_other = FDCT @ image
c_struct = FDCT.struct(c_other)


nx, nt = image.shape
# dx, dt = 0.005, 0.005 / nx * nt
# x, t = np.arange(nx) * dx, np.arange(nt) * dt
# aspect = dt / dx
# opts_plot = dict(
#     extent=(x[0], x[-1], t[-1], t[0]),
#     cmap="gray",
#     interpolation="lanczos",
#     aspect=aspect,
# )
# vmax = 0.5 * np.max(np.abs(image))
# figsize_aspect = aspect * nt / nx
# fig, ax = plt.subplots(figsize=(8, figsize_aspect * 8), sharey=True, sharex=True)
# ax.imshow(image, vmin=-vmax, vmax=vmax)
# ax.set(xlabel="Position [m]", ylabel="Time [s]", title=f"Data shape {image.shape}")
# fig.tight_layout()
# plt.show()

for j, c_scale in enumerate(c_struct, start=1):
    nangles = len(c_scale)
    rows = int(np.floor(np.sqrt(nangles)))
    cols = int(np.ceil(nangles / rows))
    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(5 * rows, nt / nx * 5 * rows),
    )
    fig.suptitle(f"Scale {j} ({len(c_scale)} wedge{'s' if len(c_scale) > 1 else ''})")
    axes = np.atleast_1d(axes).ravel()
    vmax = 0.5 * max(np.abs(Cweg).max() for Cweg in c_scale)
    for iw, (fdct_wedge, ax) in enumerate(zip(c_scale, axes), start=1):
        # Note that wedges are transposed in comparison to the input vector.
        # This is due to the underlying implementation of the transform. In
        # order to plot in the same manner as the data, we must first
        # transpose the wedge. We will using the transpose of the wedge for
        # visualization.
        c = fdct_wedge.real.T
        ax.imshow(c.T, vmin=-vmax, vmax=vmax)
        ax.set(title=f"Wedge {iw} shape {c.shape}")
        ax.axis("off")
    fig.tight_layout()

# fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=True)
# plt.colorbar(axes[0].imshow(x, cmap='gray'))
# # plt.colorbar(axes[1].imshow(y, cmap='gray'))
# # plt.colorbar(axes[2].imshow(z, cmap='gray'))
plt.show()

