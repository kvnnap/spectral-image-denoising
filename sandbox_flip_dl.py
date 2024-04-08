# import torch
# x = torch.rand(5, 3)
# print(x)

# print(torch.cuda.is_available())
# exit(0)

from utils.image import *
from evaluation.metric import *
from flip_torch.flip_loss import LDRFLIPLoss, HDRFLIPLoss
from flip_torch.data import *

import numpy as np

directory = './'
reference_filename = 'povray_reflect_caustics_8'
test_filename = 'povray_reflect_caustics_2'

# hdr_reference = load_image('smb/seeded-images/povray_reflect_caustics_8.exr', False, False)
# hdr_test = load_image('smb/seeded-images/povray_reflect_caustics_2.exr', False, False)
print('Loading images')
hdr_reference = read_exr('smb/seeded-images/povray_reflect_caustics_8.exr')
hdr_test = read_exr('smb/seeded-images/povray_reflect_caustics_2.exr')

# hdr_reference = read_exr('images/reference.exr') # EXR
# hdr_test = read_exr('images/test.exr') # EXR

# ref = HWCtoCHW(ref)
# test = HWCtoCHW(test)
pixels_per_degree = 0.30 * (1920 / 0.5313) * (np.pi / 180)

print('Computing')
hdrflip_loss_fn = HDRFLIPLoss()
hdrflip_loss = hdrflip_loss_fn(hdr_test, hdr_reference, pixels_per_degree)

print(hdrflip_loss.item())
print(round(hdrflip_loss.item(), 4) == 0.2835)
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

