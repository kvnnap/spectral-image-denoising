# import torch
# x = torch.rand(5, 3)
# print(x)

# print(torch.cuda.is_available())
# exit(0)

from utils.image import *
from evaluation.metric import *
from flip_torch.flip_loss import LDRFLIPLoss, HDRFLIPLoss
from flip_torch.data import *

import torch
import numpy as np

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

directory = './'
reference_filename = 'povray_reflect_caustics_8'
test_filename = 'povray_reflect_caustics_2'

print('Loading images')

gray = True
ldr = True
ref = load_image('smb/seeded-images/povray_reflect_caustics_8.exr', gray, ldr)
test = load_image('smb/seeded-images/povray_reflect_caustics_2.exr', gray, ldr)

ref = mem_image_to_cuda(ref, ldr)
test = mem_image_to_cuda(test, ldr)
# hdr_reference = read_exr('smb/seeded-images/povray_reflect_caustics_8.exr')
# hdr_test = read_exr('smb/seeded-images/povray_reflect_caustics_2.exr')

# hdr_reference = read_exr('images/reference.exr') # EXR
# hdr_test = read_exr('images/test.exr') # EXR

# ref = HWCtoCHW(ref)
# test = HWCtoCHW(test)
pixels_per_degree = 0.30 * (1920 / 0.5313) * (np.pi / 180)

if ldr:
    print('Computing LDR')
    ldrflip_loss_fn = LDRFLIPLoss()
    ldrflip_loss = ldrflip_loss_fn(test, ref, pixels_per_degree)
    print(ldrflip_loss.item())
else:
    print('Computing HDR')
    hdrflip_loss_fn = HDRFLIPLoss()
    hdrflip_loss = hdrflip_loss_fn(test, ref, pixels_per_degree)
    print(hdrflip_loss.item())


# print(round(hdrflip_loss.item(), 4) == 0.2835)
# print(round(hdrflip_loss.item(), 4) == 0.1597)
print('Done')

# start_exposure, stop_exposure, num_exposures = set_start_stop_num_exposures(ref)
		
# flip, exposure_map = compute_hdrflip(ref,
#                                     test,
#                                     directory=directory,
#                                     reference_filename=reference_filename,
#                                     test_filename=test_filename,
#                                     basename='basename',
#                                     default_basename=False,
#                                     #pixels_per_degree=pixels_per_degree,
#                                     # tone_mapper=tone_mapper,
#                                     start_exposure=start_exposure,
#                                     stop_exposure=stop_exposure,
#                                     num_exposures=num_exposures,
#                                     # save_ldr_images=args.save_ldr_images,
#                                     # save_ldrflip=args.save_ldrflip,
#                                     # no_magma=args.no_magma
#                                     )

# # compute_hdrflip()
# mean = "%.6f" % np.mean(flip)
# weighted_median = "%.6f" % weighted_percentile(flip, 50)
# weighted_quartile1 = "%.6f" % weighted_percentile(flip, 25)
# weighted_quartile3 = "%.6f" % weighted_percentile(flip, 75)
# minimum = "%.6f" % np.amin(flip)
# maximum = "%.6f" % np.amax(flip)

# print("\tMean: %s" % mean)
# print("\tWeighted median: %s" % weighted_median)
# print("\t1st weighted quartile: %s" % weighted_quartile1)
# print("\t3rd weighted quartile: %s" % weighted_quartile3)
# print("\tMin: %s" % minimum)
# print("\tMax: %s" % maximum)
# # command = input("Waiting before exiting")

# print('Done')

