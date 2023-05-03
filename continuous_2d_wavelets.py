from matplotlib import pyplot as plt
import numpy as np
import pywt
import py_cwt2d

from image_utils import *

img = load_image_raw_file('images/dice_2.raw')
img = convert_to_grayscale(img)
img.resize((1066,1066))
#img = alpha_correction_chain(tone_map(img))

# get an image
image = img
# image = pywt.data.camera()
# image = (image - image.min()) / (image.max() - image.min())
# set up a range of scales in logarithmic spacing between 1 and 256 (image width / 2 seems to work ehre)
ss = np.geomspace(1.0,512.0,25)
# calculate the complex pycwt and the wavelet normalizations

# wavelets = dict(
#     morlet=morlet,
#     mexh=mexh,
#     gaus=gaus,
#     gaus_2=gaus_2,
#     gaus_3=gaus_3,
#     cauchy=cauchy,
#     dog=dog
# )
coeffs, wav_norm = py_cwt2d.cwt_2d(image, ss, 'mexh')
# plot an image showing the combinations of all the scales
errors = []
N=5
fig, axes = plt.subplots(nrows=N, ncols=N, figsize=(15, 15))
for level in range(len(ss)):
    i = level // N
    j = level % N
    plt.sca(axes[i, j])
    plt.axis('off')
    # C = 1.0 / (ss[:level] * wav_norm[:level])
    # reconstruction = (C * np.real(coeffs[..., :level])).sum(axis=-1)
    C = 1.0 / (ss[level] * wav_norm[level])
    reconstruction = (C * np.real(coeffs[..., level]))
    reconstruction = 1.0 - (reconstruction - reconstruction.min()) / (reconstruction.max() - reconstruction.min())
    errors.append(np.sqrt(np.sum(np.power(reconstruction - image, 2.0))))
    plt.imshow(reconstruction, cmap='gray')
plt.show()
fig2, ax2 = plt.subplots(nrows=1, ncols=1, figsize=(6, 6/1.618))
plt.plot(errors, label='norm')
plt.xlabel('Number of Reconstruction Scales')
plt.ylabel('Reconstruction Error')
plt.show()