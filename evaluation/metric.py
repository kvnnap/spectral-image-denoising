import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr

def local_mse(ref, noisy):
    return np.sum((ref - noisy) ** 2).item()

# def luma(image):
#     return (0.299 * image[:, :, 2] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 0]).astype(np.uint8)

def get_data_range(ref, noisy):
    max_value = max(ref.max(), noisy.max())
    min_value = min(ref.min(), noisy.min())
    return max_value - min_value

def local_psnr_old(ref, noisy):
    mse = local_mse(ref, noisy)
    #mse = np.mean((ref.astype(np.float64) / 255 - noisy.astype(np.float64) / 255) ** 2)
    if mse == 0:
        return float('inf')
    range = get_data_range(ref, noisy)
    psnr = 10 * np.log10(range ** 2 / mse)
    return psnr

def local_psnr(ref, noisy):
    range = get_data_range(ref, noisy)
    if (range == 0):
        return float('inf')
    return -psnr(ref, noisy, data_range=range)

def local_ssim(ref, noisy):
    range = get_data_range(ref, noisy)
    if (range == 0):
        return 0
    return -ssim(ref, noisy, data_range=range, channel_axis=2).item()

def local_mse_ssim(ref, noisy):
    return local_mse(ref, noisy) + local_ssim(ref, noisy)

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
        else:
            raise ValueError(f"Invalid metric name {metricName}")
