from matplotlib import pyplot as plt
import numpy as np
import curvelops as cl
import pywt

from utils.image import *

fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True)


x = load_image_raw_file('images/dice_2.raw')
#x = load_image_raw_file('images/ashtray_2.raw')
x = convert_to_grayscale(x)
#x = alpha_correction_chain(tone_map(x))

FDCT = cl.FDCT2D(dims=x.shape)
c = FDCT @ x

for i in range(4):
    c = pywt.threshold(c, 0.0125 * i, mode='hard')
    xinv = (FDCT.H @ c).real
    xinv = alpha_correction_chain(tone_map(xinv))
    axes[i >> 1, i % 2].imshow(xinv, cmap='gray')
    axes[i >> 1, i % 2].set_title(i)


# x = alpha_correction_chain(tone_map(x))
# xinv = alpha_correction_chain(tone_map(xinv))

plt.show()

# structured = FDCT.struct(c)
# structured = 0
# x = np.random.randn(100, 50)
# FDCT = cl.FDCT2D(dims=x.shape)
# c = FDCT @ x
# structured = FDCT.struct(c)
# my_x = FDCT.vect(structured)
# xinv = FDCT.H @ c
# np.testing.assert_allclose(x, xinv)

