import numpy as np
import hdrpy
import matlab
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import mean_squared_error as mse_fn
from utils.image import get_channel_count

def local_mse(ref, noisy):
    #return np.mean((ref - noisy) ** 2).item()
    return mse_fn(ref, noisy).item()

def get_data_range(ref, noisy):
    max_value = max(ref.max(), noisy.max())
    min_value = min(ref.min(), noisy.min())
    return max_value - min_value

def local_psnr_old(ref, noisy):
    mse = local_mse(ref, noisy)
    range = get_data_range(ref, noisy)
    if mse == 0 or range == 0:
        return float('-inf')
    psnr = 10 * np.log10(range ** 2 / mse)
    return -psnr.item()

def local_psnr(ref, noisy):
    range = get_data_range(ref, noisy)
    if (range == 0):
        return float('-inf')
    return -psnr(ref, noisy, data_range=range).item()

def local_ssim(ref, noisy):
    range = get_data_range(ref, noisy)
    if (range == 0):
        return -1.0
    return -ssim(ref, noisy, data_range=range, channel_axis=2).item()

def local_mse_ssim(ref, noisy):
    return local_mse(ref, noisy) + local_ssim(ref, noisy)

# try:
h = hdrpy.initialize()
# 24 inch Full HD display, observed from 30cm distance
ppd = h.hdrvdp_pix_per_deg(24.0, matlab.double([1920, 1080]), 0.30)

# except Exception as e:
#     print('Error initializing hdrvdp3 package\\n:{}'.format(e))
#     exit(1)
def local_hdrvdp3(ref, noisy):
    s = 'luma-display' if get_channel_count(noisy) == 1 else 'rgb-native'
    result = h.hdrvdp3('side-by-side', noisy, ref, s, ppd, ['quiet', True])
    return -result['Q']

class MetricFactory:
    @staticmethod
    def create(metricName):
        name = metricName.strip().lower()
        if (name == "mse"):
            return local_mse
        elif(name == "ssim"):
            return local_ssim
        elif(name == "mse_ssim"):
            return local_mse_ssim
        elif(name == "psnr"):
            return local_psnr
        elif(name == "hdrvdp3"):
            return local_hdrvdp3
        else:
            raise ValueError(f"Invalid metric name {metricName}")
