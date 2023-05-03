from matplotlib import pyplot as plt
import numpy as np
import pywt
import py_cwt2d

from image_utils import *

def pad(A, shape):
   out = np.zeros(shape)
   out[tuple(slice(0, d) for d in np.shape(A))] = A
   return out

img = load_image_raw_file('images/dice_2.raw')
img = convert_to_grayscale(img)
img = alpha_correction_chain(tone_map(img))
min_dim = min(img.shape)
max_dim = max(img.shape)
img = pad(img, (max_dim,max_dim))
#img = img[0:600,0:600]
#img = np.resize(img,(600,600))

# get an image
image = img
# image = pywt.data.camera()
# image = (image - image.min()) / (image.max() - image.min())
# set up a range of scales in logarithmic spacing between 1 and 256 (image width / 2 seems to work ehre)
ss = np.geomspace(1.0,min_dim,25)
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
fig, axes = plt.subplots(nrows=N, ncols=N, figsize=(15, 15), sharex=True, sharey=True)
for level in range(len(ss)):
    i = level // N
    j = level % N
    plt.sca(axes[i, j])
    plt.axis('off')
    if True:
        C = 1.0 / (ss[:level] * wav_norm[:level])
        reconstruction = (C * np.real(coeffs[..., :level])).sum(axis=-1)
    else:
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