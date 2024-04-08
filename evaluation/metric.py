import numpy as np
import hdrpy
import matlab
import torch

from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import mean_squared_error as mse_fn
from utils.image import get_channel_count
from flip_torch.flip_loss import LDRFLIPLoss, HDRFLIPLoss
from flip.data import HWCtoCHW
from flip.flip_api import compute_ldrflip, compute_hdrflip
from flip.flip import set_start_stop_num_exposures

def local_mse(ref, noisy, dpString):
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

def local_psnr(ref, noisy, dpString):
    range = get_data_range(ref, noisy)
    if (range == 0):
        return float('-inf')
    return -psnr(ref, noisy, data_range=range).item()

def local_ssim(ref, noisy, dpString):
    range = get_data_range(ref, noisy)
    if (range == 0):
        return -1.0
    return -ssim(ref, noisy, data_range=range, channel_axis=2).item()

def local_mse_ssim(ref, noisy, dpString):
    return local_mse(ref, noisy) + local_ssim(ref, noisy)

# try:
h = hdrpy.initialize()
# 24 inch Full HD display, observed from 30cm distance
ppd = h.hdrvdp_pix_per_deg(24.0, matlab.double([1920, 1080]), 0.30)

# except Exception as e:
#     print('Error initializing hdrvdp3 package\\n:{}'.format(e))
#     exit(1)

# if (ref.flags.contiguous == False and ref.flags.c_contiguous == False and ref.flags.f_contiguous == False) or (noisy.flags.contiguous == False and noisy.flags.c_contiguous == False and noisy.flags.f_contiguous == False):
# if (ref.flags.contiguous == False) or (noisy.flags.contiguous == False):
#     print('oops')
def local_hdrvdp3(ref, noisy, dpString):
    imgLoader = dpString.imageLoader.strip().lower()
    selector = { 
        'gray': 'luminance', 
        'gray_tm': 'luma-display',
        'rgb': 'rgb-native',
        'rgb_tm': 'sRGB-display'
    }
    s = selector[imgLoader]
    noisy = np.ascontiguousarray(noisy)
    ref = np.ascontiguousarray(ref)
    noisy = matlab.single(noisy) if noisy.dtype == np.float32 else matlab.double(noisy)
    ref = matlab.single(ref) if ref.dtype == np.float32 else matlab.double(ref)
    result = h.hdrvdp3('side-by-side', noisy, ref, s, ppd, ['use_gpu', False, 'quiet', True])
    return -result['Q']

def mem_image_to_cuda(img_np, is_ldr):
    if get_channel_count(img_np) == 1:
        img_np = np.repeat(img_np, 3, axis=2)
    if is_ldr:
        # img_np = np.rollaxis(img_np, 2)
        # return torch.from_numpy(img_np).unsqueeze(0).cuda()
        return torch.from_numpy(img_np).permute(2, 0, 1).unsqueeze(0).cuda()
    else:
        img_torch = torch.max(torch.nan_to_num(torch.from_numpy(np.array(img_np))), torch.tensor([0.0])).cuda() # added maximum to avoid negative values in images
        return img_torch.permute(2, 0, 1).unsqueeze(0)

def mem_image_to_flip(img_np):
    if get_channel_count(img_np) == 1:
        img_np = np.repeat(img_np, 3, axis=2)
    return HWCtoCHW(img_np)

def local_flip(ref, noisy, dpString):
    if ref.dtype != np.float32:
        ref = ref.astype(np.float32)
    if noisy.dtype != np.float32:
        noisy = noisy.astype(np.float32)
    imgLoader = dpString.imageLoader.strip().lower()
    isLdr = imgLoader.endswith('_tm')
    isGPU = torch.cuda.is_available()
    # pixels_per_degree = 0.30 * (1920 / 0.5313) * (np.pi / 180)
    pixels_per_degree = ppd

    if isGPU:
        ref = mem_image_to_cuda(ref, isLdr)
        noisy = mem_image_to_cuda(noisy, isLdr)
        loss_fn = LDRFLIPLoss() if isLdr else HDRFLIPLoss()
        flip_loss = loss_fn(noisy, ref, pixels_per_degree)
        score = flip_loss.item()
    else:
        ref = mem_image_to_flip(ref)
        noisy = mem_image_to_flip(noisy)
        if isLdr:
            flip = compute_ldrflip(ref, noisy, pixels_per_degree).squeeze(0)
        else:
            directory = './'
            # reference_filename = 'povray_reflect_caustics_8'
            # test_filename = 'povray_reflect_caustics_2'
            start_exposure, stop_exposure, num_exposures = set_start_stop_num_exposures(ref)
            flip, exposure_map = compute_hdrflip(ref,
                                        noisy,
                                        directory=directory,
                                        reference_filename='reference_filename',
                                        test_filename='test_filename',
                                        basename='basename',
                                        default_basename=False,
                                        pixels_per_degree=pixels_per_degree,
                                        # tone_mapper=tone_mapper,
                                        start_exposure=start_exposure,
                                        stop_exposure=stop_exposure,
                                        num_exposures=num_exposures,
                                        # save_ldr_images=args.save_ldr_images,
                                        # save_ldrflip=args.save_ldrflip,
                                        # no_magma=args.no_magma
                                        )
        score = np.mean(flip)
    return score

class MetricFactory:
    @staticmethod
    def create(metricName):
        name = metricName.strip().lower()
        if name == "mse":
            return local_mse
        elif name == "ssim":
            return local_ssim
        elif name == "mse_ssim":
            return local_mse_ssim
        elif name == "psnr":
            return local_psnr
        elif name == "hdrvdp3":
            return local_hdrvdp3
        elif name == "flip":
            return local_flip
        else:
            raise ValueError(f"Invalid metric name {metricName}")
