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

    # Convert the 2D numpy array to one with shape (height, width, 1) (remove braces to get 2d shape)
    return grayscale_data[:, :, np.newaxis]

def tone_map(image_data):
    # Perform tone mapping on the pixel data using the formula x/(x+1)
    tone_mapped_data = image_data / (image_data + 1)

    # Return the tone mapped pixel data
    return tone_mapped_data

def load_image(path, gray = True, tm = True):
    image = load_image_raw_file(path)
    if (gray):
        image = convert_to_grayscale(image)
    if (tm):
        image = alpha_correction_chain(tone_map(image))
    return image

def get_channel_count(image):
    return image.shape[2] if (len(image.shape) > 2) else 1

def seperate_channels(image):
    if (len(image.shape) > 2):
        return [image[:,:,i] for i in range(0, get_channel_count(image))]
    else:
        return [image]
    
def merge_channels(imageArray):
    return np.stack(imageArray, axis=2)

def alpha_correction_chain(data):
    gamma = 2.4
    encoding_gamma = 1 / gamma
    correction_data = np.array(data)
    correction_data = np.where(correction_data <= 0.0031308, 12.92*correction_data, 1.055*np.power(correction_data, encoding_gamma) - 0.055)
    return correction_data

def tone_alpha_map(image):
    return alpha_correction_chain(tone_map(image)) if image is not None else None

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

# Uses SURE to estimate the mean-squared error
def estimate_mse(image):
    # Convert image to a flattened array
    image_flattened = image.flatten()

    # Compute the mean-squared error (MSE) using SURE
    d = image_flattened.size
    expected_value = np.mean(image_flattened)
    mse = np.mean((image_flattened - expected_value)**2) + (d - 1) * np.var(image_flattened)

    return mse

soft = lambda x, t : np.sign(x) * np.maximum(np.abs(x) - t, 0)

# x is the original, y is estimate
TrueMSE = lambda x, y : np.sum((x - y)**2)

# y = x + n, t is the thresolding value for soft thresholding, sig is std of noise
SureSoftMSE = lambda y, t, sig : ( np.sum(y[np.abs(y) < t]**2) 
    + np.sum(np.abs(y) > t) * (t**2 + 2 * sig**2) - sig**2 * y.size )

# SureSoftMSE = lambda y, t, sig: (
#     np.sum(np.where(np.abs(y) < t, y ** 2, (t ** 2 + 2 * sig ** 2) * np.abs(y) - (t ** 2 - sig ** 2)))
# )

# def SureSoftMSE(y, t, sig):
#     return y.size - 2 * np.sum(np.where(np.abs(y) <= t, 1, 0)) + np.sum(np.where(np.abs(y) <= t, 0, np.sign(y) * (np.abs(y) - t))**2)

# works only with positive numbers?
def next_power_of_two(n):
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    n |= n >> 32
    return n + 1

def resize_to_nearest_power_of_2_square(img):
    s = next_power_of_two(max(img.shape))
    return np.pad(img, ((0, s - img.shape[0]), (0, s - img.shape[1])), mode='constant')

def crop_enlarge(img, shape):
    # Cropping
    if (shape[0] < img.shape[0]):
        img = img[:shape[0], :, :]
    if (shape[1] < img.shape[1]):
        img = img[:, :shape[1], :]
    # Enlargement
    return np.pad(img, ((0, shape[0] - img.shape[0]), (0, shape[1] - img.shape[1]), (0, 0)), mode='constant')
