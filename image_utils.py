import numpy as np

def load_image_raw_file(file_path):
    with open(file_path, 'rb') as f:
        # Read the first two integers as the width and height
        width, height = np.frombuffer(f.read(8), dtype=np.uint32)

        # Read the rest of the file as the RGB pixel values in float format
        pixel_data = np.frombuffer(f.read(), dtype=np.float32)

        # Reshape the pixel data into a 3D numpy array with shape (height, width, 3)
        pixel_data = pixel_data.reshape((height, width, 3))

    return pixel_data

def convert_to_grayscale(image_data):
    # Convert RGB pixel data to grayscale using the formula:
    # Y = 0.299*R + 0.587*G + 0.114*B
    # See https://en.wikipedia.org/wiki/Grayscale#Converting_color_to_grayscale for more information
    grayscale_data = 0.299*image_data[:,:,0] + 0.587*image_data[:,:,1] + 0.114*image_data[:,:,2]

    # Convert the pixel data to a 2D numpy array and return it
    return grayscale_data

def tone_map(image_data):
    # Perform tone mapping on the pixel data using the formula x/(x+1)
    tone_mapped_data = image_data / (image_data + 1)

    # Return the tone mapped pixel data
    return tone_mapped_data

import numpy as np

def alpha_correction_chain(data):
    gamma = 2.4
    encoding_gamma = 1 / gamma
    correction_data = np.array(data)
    correction_data = np.where(correction_data <= 0.0031308, 12.92*correction_data, 1.055*np.power(correction_data, encoding_gamma) - 0.055)
    return correction_data

def float_image_to_uint(data):
    # Clip the pixel values to the range [0, 255] and convert to unsigned 8-bit integers
    return np.clip(255 * data, 0, 255).astype(np.uint8)

def filter_image_salt(img, scale):
    height, width = img.shape
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            s = [img[i-1, j-1], img[i-1, j], img[i-1, j+1], img[i, j-1], img[i, j+1], img[i+1, j-1], img[i+1, j], img[i+1, j+1]]
            pix = img[i, j]
            if pix > scale * max(s):
                img[i, j] = np.mean(s)

