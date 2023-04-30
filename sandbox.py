import matplotlib.pyplot as plt

from image_utils import *

raw_image = load_image_raw_file('images/dice_2.raw')
raw_image = convert_to_grayscale(raw_image)
# tone_mapped = tone_map(raw_image)
# alpha_image = alpha_correction_chain(tone_mapped)
# data = float_image_to_uint(alpha_image)

im = plt.imshow(raw_image, cmap='hot')
cbar = plt.colorbar(im)
#cbar.set_label("color")
plt.show()