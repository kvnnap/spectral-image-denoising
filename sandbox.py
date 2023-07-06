import matplotlib.pyplot as plt

from image_utils import *

ref_image = load_image_raw_file('images/cb_caustics/output_0.raw')
ref_image = convert_to_grayscale(ref_image)
ref_image = alpha_correction_chain(tone_map(ref_image))
refi_std = np.std(ref_image)

raw_image = load_image_raw_file('images/cb_caustics/output_1.raw')
raw_image = convert_to_grayscale(raw_image)
raw_image = alpha_correction_chain(tone_map(raw_image))
rawi_std = np.std(raw_image)


# tone_mapped = tone_map(raw_image)
# alpha_image = alpha_correction_chain(tone_mapped)
# data = float_image_to_uint(alpha_image)


thold = np.linspace(0, 4, 100) 
MSEcurve = np.zeros(thold.size)
SUREcurve = np.zeros(thold.size)
for ind, t  in enumerate(thold):
    z = soft(raw_image, t)
    MSEcurve[ind] = TrueMSE(z, ref_image)
    SUREcurve[ind] = SureSoftMSE(raw_image, t, rawi_std)

fig, ax = plt.subplots(1,1, figsize = (10,5))
ax.plot(thold, MSEcurve, label = 'True MSE')
ax.plot(thold, SUREcurve, label = 'SURE')
ax.legend()
ax.set_xlabel(r'Threshold / $\sigma^2$')
ax.set_title('MSE with respect to Threshold Value in the Soft Threshold')
ax.grid()

print("done")

print(estimate_mse(raw_image))

# im = plt.imshow(raw_image, cmap='gray')
# cbar = plt.colorbar(im)
# #cbar.set_label("color")
plt.show()

import numpy as np

# Generate the true signal
x = np.array([1, 2, 3, 4, 5])

# Add noise to create the observed signal
noise = np.random.normal(0, 1, size=x.shape)  # Gaussian noise
y = x + noise

# Define the estimator (example: simple averaging)
estimator = np.mean(y)

# Compute the SURE estimate of the MSE
d = y.size  # Dimensionality of the problem
residuals = estimator - y  # Residuals of the estimator
correction = np.mean(residuals ** 2) - np.var(noise)  # Correction term
sure_estimate = np.mean(residuals ** 2) - d * correction

print("SURE estimate of MSE:", sure_estimate)