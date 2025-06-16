import numpy as np
import OpenEXR
import Imath
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from skimage.transform import resize

from utils.array import sanitise
from utils.string import extract_file_extension, concat_paths

BASE_PATH = ''

def set_base_path(base_path):
    global BASE_PATH
    BASE_PATH = base_path

def get_base_path():
    return BASE_PATH

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
    channels = list(header['channels'].keys())
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
    # clip to sane ranges
    image_array = np.clip(image_array, 0, 1) * 255

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
    #grayscale_data = 0.299*image_data[:,:,0] + 0.587*image_data[:,:,1] + 0.114*image_data[:,:,2]
    grayscale_data = 0.2126729*image_data[:,:,0] + 0.7151522*image_data[:,:,1] + 0.0721750*image_data[:,:,2]

    # Convert the 2D numpy array to one with shape (height, width, 1) (remove braces to get 2d shape)
    return grayscale_data[:, :, np.newaxis]

def tone_map(image_data):
    # Perform tone mapping on the pixel data using the formula x/(x+1)
    tone_mapped_data = image_data / (image_data + 1)

    # Return the tone mapped pixel data
    return tone_mapped_data

def saturate(x):
    return np.clip(x, 0.0, 1.0)

def tone_map_aces(x):
    x *= 0.6
    a = 2.51
    b = 0.03
    c = 2.43
    d = 0.59
    e = 0.14
    return saturate((x * (a * x + b)) / (x * (c * x + d) + e))

def crop_image(image, pos, size):
    x_start, y_start = pos[0], pos[1]
    x_end, y_end = x_start + size[0], y_start + size[1]
    cropped_image = image[y_start:y_end, x_start:x_end, :]
    return cropped_image

def resize_image(image, scale_factor):
    # Resize the image to the specified size
    new_height = int(image.shape[0] * scale_factor)
    new_width = int(image.shape[1] * scale_factor)
    return resize(image, (new_height, new_width), order=5)

def blur_image(image, sigma):
    # Apply a Gaussian blur to the image
    return gaussian_filter(image, sigma, mode='nearest')

def load_image_from_file(path):
    # Select image format
    path = concat_paths(BASE_PATH, path)
    file_extension = extract_file_extension(path).lower()
    return load_image_raw_file(path) if file_extension != '.exr' else load_exr_image(path)

def process_loaded_image(image, gray = True, tm = True, gamma = True, tm_fn = tone_map, config = None):
    # Load the image from file
    # Added for 3rd paper
    if config:
        crop = config.get('crop')
        blur = config.get('blur')
        downsample = config.get('downsample')
    else:
        crop = False
        blur = False
        downsample = False
    image = sanitise(image)
    if crop:
        image = crop_image(image, crop['pos'], crop['size'])
    if downsample:
        image = resize_image(image, config['downsample'])
    if blur:
        image = blur_image(image, config['blur'])
    if gray:
        image = convert_to_grayscale(image)
    if tm:
        image = tm_fn(image)
        if gamma:
            image = alpha_correction_chain(image)
    return image

def load_image(path, gray = True, tm = True, gamma = True, tm_fn = tone_map, config = None):
    return process_loaded_image(load_image_from_file(path), gray, tm, gamma, tm_fn, config)

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

def interpolate_image_to_range(image, im_range=(0, 1)):
    return np.interp(image, (image.min(), image.max()), im_range)

# returns slices only
def get_crop_image_border_slice(image):
    # Find the first and last rows where all values are zero
    first_row = 0
    last_row = image.shape[0]
    for row in range(image.shape[0]):
        if np.all(image[row, :] == 0):
            first_row = row + 1
        else:
            break
    for row in range(image.shape[0]-1, -1, -1):
        if np.all(image[row, :] == 0):
            last_row = row
        else:
            break
    
    # Find the first and last columns where all values are zero
    first_col = 0
    last_col = image.shape[1]
    for col in range(image.shape[1]):
        if np.all(image[:, col] == 0):
            first_col = col + 1
        else:
            break
    for col in range(image.shape[1]-1, -1, -1):
        if np.all(image[:, col] == 0):
            last_col = col
        else:
            break
    
    # Crop the image using the calculated indices
    return ([first_row, last_row], [first_col, last_col])
