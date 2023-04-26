import matplotlib.pyplot as plt
import numpy as np
import pywt

# Load the image as a NumPy array
image = plt.imread("images/dice_2.png")

# Define the wavelet packet decomposition parameters
level = 2  # The level of decomposition
wavelet = 'haar'  # The wavelet to use

# Perform the wavelet packet decomposition
wp = pywt.WaveletPacket2D(data=image, wavelet=wavelet, mode='symmetric', maxlevel=level)

# Plot the wavelet packet decomposition
fig, axes = plt.subplots(nrows=2**level, ncols=2**level)


# for i, node in enumerate(wp.get_level(level)):
#     row = int(i / (2**level))
#     col = i % (2**level)
#     if i > 0:
#         node.data = pywt.threshold(node.data, 0.1, mode='soft')
#     axes[row, col].imshow(node.data, cmap=plt.cm.gray)
#     axes[row, col].title.set_text(node.path)
#     axes[row, col].axis('off')



for row, nodeRows in enumerate(wp.get_level(level, order='freq')):
    for col, node in enumerate(nodeRows):
        if row > 0 or col > 0:
            node.data = pywt.threshold(node.data, 0.1*10**row, mode='hard')
        axes[row, col].imshow(node.data, cmap=plt.cm.gray)
        axes[row, col].title.set_text(node.path)
        # axes[row, col].axis('off')
plt.show()


rec = wp.reconstruct(update=True)
plt.imshow(rec, cmap=plt.cm.gray)
plt.show()