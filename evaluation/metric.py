import numpy as np
from skimage.metrics import structural_similarity as ssim

def local_mse(ref, noisy):
    return np.sum((ref - noisy) ** 2)

def local_ssim(ref, noisy):
    return ssim(ref, noisy, data_range=noisy.max() - noisy.min())

class MetricFactory:
    @staticmethod
    def create(metricName):
        name = metricName.strip().lower()
        if (name == "mse"):
            return local_mse
        elif(name == "ssim"):
            return local_ssim
        else:
            raise ValueError(f"Invalid metric name {metricName}")
