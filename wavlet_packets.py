import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pywt

# Load the image as a NumPy array
#image = plt.imread("images/dice_2.png")
# Load image
img = Image.open('images/dice_2.png')

# Convert to grayscale
img_gray = img.convert('L')

img_gray = np.array(img_gray)

# Define the wavelet packet decomposition parameters
level = 4  # The level of decomposition
wavelet = 'sym2'  # The wavelet to use

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
        # if row > 2 or col > 2:
        #     node.data = pywt.threshold(node.data, 100000, mode='hard')
        if row > 0 or col > 0:
            for img in [node.data]:
                s = np.std(img)
                m = np.mean(img)
                mask = np.logical_and(img >= m - (1 * row + 0 * col) * sigma * s, img <= m + (1 * row + 0 * col) * sigma * s)
                img[~mask] = m
        # axes[row, col].imshow(node.data, cmap=plt.cm.gray)
        # axes[row, col].title.set_text(node.path)
        # axes[row, col].axis('off')
#plt.show()


fig, axes = plt.subplots(nrows=2)
axes[0].imshow(img_gray, cmap=plt.cm.gray)

rec = wp.reconstruct(update=True)
axes[1].imshow(rec, cmap=plt.cm.gray)

#plt.imshow(rec, cmap=plt.cm.gray)
plt.show()