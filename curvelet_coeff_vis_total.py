import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pylops.signalprocessing import FFT2D

from curvelops import FDCT2D
from curvelops.plot import (
    create_axes_grid,
    create_inset_axes_grid,
    overlay_arrows,
    overlay_disks,
)
from curvelops.utils import array_split_nd, ndargmax

from utils.image import *


ref_image = load_image('images/dice_caustics/output_0.raw', True)[:, :, 0]
image = ref_image
#image = image.T
Cop = FDCT2D(dims=image.shape, nbscales=4, allcurvelets=False)
#t = Cop @ image
#d_c = Cop.struct(t)
d_c = [[np.zeros(s) for s in shape] for shape in Cop.shapes]

#c_struct = d_c

count = 0
for scale_index, scale in enumerate(d_c):
    for wedge_index in range(len(scale)):
        count += 1
        # d_c[scale_index][wedge_index] = np.full_like(d_c[scale_index][wedge_index], count)
        d_c[scale_index][wedge_index] = np.full((1, 1), complex(count))
        #d_c[scale_index][wedge_index] = count

rows, cols = 1, 1
fig, axes = create_axes_grid(
    rows,
    cols,
    kwargs_subplots=dict(projection="polar"),
    kwargs_figure=dict(figsize=(4, 4)),
)
overlay_disks(d_c, axes, annotate=True, cmap='gray')

plt.show()