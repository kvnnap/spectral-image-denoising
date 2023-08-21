import matplotlib.pyplot as plt

from utils.image import *

ref_image = load_image_raw_file('images/cb_caustics/output_0.raw')
ref_image = convert_to_grayscale(ref_image)
ref_image = alpha_correction_chain(tone_map(ref_image))
refi_std = np.std(ref_image)

image_count = 15
MSEcurve = np.zeros(image_count)
for i in range(1, image_count):
    raw_image = load_image_raw_file('images/cb_caustics/output_' + str(i) + '.raw')
    raw_image = convert_to_grayscale(raw_image)
    raw_image = alpha_correction_chain(tone_map(raw_image))
    rawi_std = np.std(raw_image)
    MSEcurve[i - 1] = TrueMSE(raw_image, ref_image)


fig, ax = plt.subplots(1,1, figsize = (10,5))
ax.plot(range(0, image_count), MSEcurve, label = 'True MSE')
ax.legend()
ax.set_xlabel('Image number')
ax.set_title('MSE with respect to Threshold Value in the Soft Threshold')
ax.grid()
plt.show()
