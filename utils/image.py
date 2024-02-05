import numpy as np
import OpenEXR
import Imath
import matplotlib.pyplot as plt

from utils.string import extract_file_extension, concat_paths

BASE_PATH = ''

def set_base_path(base_path):
    global BASE_PATH
    BASE_PATH = base_path

def load_image_raw_file(file_path):
    with open(file_path, 'rb') as f:
        # Read the first two integers as the width and height
        width, height = np.frombuffer(f.read(8), dtype=np.uint32)

        # Read the rest of the file as the RGB pixel values in float format
        pixel_data = np.frombuffer(f.read(), dtype=np.float32)

        # Reshape the pixel data into a 3D numpy array with shape (height, width, 3)
        pixel_data = pixel_data.reshape((height, width, 3))

    return pixel_data

def load_exr_image(file_path):
    exr_file = OpenEXR.InputFile(file_path)
    header = exr_file.header()

    # Get image attributes
    width = int(header['dataWindow'].max.x - header['dataWindow'].min.x + 1)
    height = int(header['dataWindow'].max.y - header['dataWindow'].min.y + 1)

    # Read RGB channels with full floating-point precision
    channels = ['R', 'G', 'B']
    pixel_type = Imath.PixelType(Imath.PixelType.FLOAT)
    
    # Read channels and convert to numpy arrays
    channel_data = {channel: exr_file.channel(channel, pixel_type) for channel in channels}

    # Combine channels into an image array
    image_array = np.zeros((height, width, len(channels)), dtype=np.float32)
    for i, channel in enumerate(channels):
        image_array[:, :, i] = np.frombuffer(channel_data[channel], dtype=np.float32).reshape((height, width))

    return image_array

def save_image_as_exr(image_array, file_path):
    # Convert the image array to uint8 format
    rgb_array = np.array(image_array, dtype=np.float32)

    # Create an OpenEXR header with FLOAT pixel type
    header = OpenEXR.Header(rgb_array.shape[1], rgb_array.shape[0])

    num_channels = rgb_array.shape[2]

    header['channels'] = dict(('RGB'[i], Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))) for i in range(num_channels))

    # Create an OpenEXR output file
    exr_file = OpenEXR.OutputFile(file_path, header)

    # Write the RGB data to the file
    exr_file.writePixels(dict(('RGB'[i], rgb_array[:,:,i].tobytes()) for i in range(num_channels)))

    # Close the file
    exr_file.close()

def save_image_as_png(image_array, file_path):
    # Convert the image array to uint8 format
    image_array = np.array(image_array, dtype=np.uint8)

    # Reshape the image array if it has a singleton dimension
    if image_array.shape[-1] == 1:
        image_array = np.squeeze(image_array, axis=-1)

    # Save
    plt.imsave(file_path, image_array, cmap='gray')

def save_image(image_array, file_path):
    save_image_as_png(image_array, file_path + '.png')
    save_image_as_exr(image_array, file_path + '.exr')


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
    # Select image format
    path = concat_paths(BASE_PATH, path)
    file_extension = extract_file_extension(path).lower()
    image = load_image_raw_file(path) if file_extension != '.exr' else load_exr_image(path)
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

def list_to_square_image(arr, pix_size=480):
    # Determine the size of the square image
    N = len(arr)
    side_length = round(N**0.5)  # Take the square root and round to the nearest integer

    pix_size = (pix_size, pix_size) # Can do rects too if pix_size is not square

    pix_size = tuple(np.maximum((side_length, side_length), pix_size))
    ppv  = (pix_size[0] / side_length, pix_size[1] / side_length)

    # Create a square array filled with zeros
    square_image = np.zeros(pix_size)

    # Fill the array with coeff values
    for i, value in enumerate(arr):
        row = i // side_length
        col = i % side_length
        square_image[int(row * ppv[0]) : int((row + 1) * ppv[0]), int(col * ppv[1]) : int((col + 1) * ppv[1])] = value
        
    return square_image

def interpolate_image_to_range(image, im_range=(0, 255)):
    return np.interp(image, (image.min(), image.max()), im_range)
