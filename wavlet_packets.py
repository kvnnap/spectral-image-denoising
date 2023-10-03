import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pywt

from utils.image import *

# Load the image as a NumPy array
#image = plt.imread("images/dice_2.png")
# Load image
img = load_image_raw_file('images/dice_2.raw')
img_gray = convert_to_grayscale(img)[:, :, 0]

# Define the wavelet packet decomposition parameters
level = 5  # The level of decomposition
wavelet = 'haar'  # The wavelet to use

# Perform the wavelet packet decomposition
wp = pywt.WaveletPacket2D(data=img_gray, wavelet=wavelet, mode='symmetric', maxlevel=level)

# Plot the wavelet packet decomposition
#fig, axes = plt.subplots(nrows=2**level, ncols=2**level)


# for i, node in enumerate(wp.get_level(level)):
#     row = int(i / (2**level))
#     col = i % (2**level)
#     if i > 0:
#         node.data = pywt.threshold(node.data, 0.1, mode='soft')
#     axes[row, col].imshow(node.data, cmap=plt.cm.gray)
#     axes[row, col].title.set_text(node.path)
#     axes[row, col].axis('off')

sigma = 1

for row, nodeRows in enumerate(wp.get_level(level, order='freq')):
    for col, node in enumerate(nodeRows):
        if not(row == 31 and col == 31):
            node.data = np.zeros_like(node.data)
        else:
            mask = np.zeros_like(node.data, dtype=bool)
            mask[0:1,0:1]=True
            node.data[~mask] = 0
        # node.data = pywt.threshold(node.data, 1)
        # if row > 0 or col > 0:
        #     for img in [node.data]:
        #         s = np.std(img)
        #         m = np.mean(img)
        #         mask = np.logical_and(img >= m - (1 * row + 0 * col) * sigma * s, img <= m + (1 * row + 0 * col) * sigma * s)
        #         img[~mask] = m
        # axes[row, col].imshow(node.data, cmap=plt.cm.gray)
        # axes[row, col].title.set_text(node.path)
        # axes[row, col].axis('off')
#plt.show()


fig, axes = plt.subplots(nrows=2)
#img_gray = alpha_correction_chain(tone_map(img_gray))
plt.colorbar(axes[0].imshow(img_gray, cmap=plt.cm.gray))

rec = wp.reconstruct(update=True)
#rec -= rec.min()
#rec = alpha_correction_chain(tone_map(rec))
#rec = np.abs(rec)
plt.colorbar(axes[1].imshow(rec, cmap=plt.cm.gray))

#plt.imshow(rec, cmap=plt.cm.gray)
plt.show()