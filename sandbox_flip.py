import sys
import os

#sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/flip')

from utils.image import *
from evaluation.metric import *
from flip.flip_api import *
from flip.data import *
from flip.flip import *

import numpy as np

def mem_image_to_flip(img_np):
    if get_channel_count(img_np) == 1:
        img_np = np.repeat(img_np, 3, axis=2)
    return HWCtoCHW(img_np)

directory = './'
reference_filename = 'povray_reflect_caustics_8'
test_filename = 'povray_reflect_caustics_2'

print('Loading images')

gray = True
ldr = True
ref = load_image('smb/seeded-images/povray_reflect_caustics_8.exr', gray, ldr)
test = load_image('smb/seeded-images/povray_reflect_caustics_2.exr', gray, ldr)

ref = mem_image_to_flip(ref)
test = mem_image_to_flip(test)

pixels_per_degree = 0.30 * (1920 / 0.5313) * (np.pi / 180)
start_exposure, stop_exposure, num_exposures = set_start_stop_num_exposures(ref)

if not ldr:
    flip, exposure_map = compute_hdrflip(ref,
                                        test,
                                        directory=directory,
                                        reference_filename=reference_filename,
                                        test_filename=test_filename,
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
else:
    flip = compute_ldrflip(ref,
                            test,
                            pixels_per_degree=pixels_per_degree
                            ).squeeze(0)

# compute_hdrflip()
mean = "%.6f" % np.mean(flip)
weighted_median = "%.6f" % weighted_percentile(flip, 50)
weighted_quartile1 = "%.6f" % weighted_percentile(flip, 25)
weighted_quartile3 = "%.6f" % weighted_percentile(flip, 75)
minimum = "%.6f" % np.amin(flip)
maximum = "%.6f" % np.amax(flip)

print("\tMean: %s" % mean)
print("\tWeighted median: %s" % weighted_median)
print("\t1st weighted quartile: %s" % weighted_quartile1)
print("\t3rd weighted quartile: %s" % weighted_quartile3)
print("\tMin: %s" % minimum)
print("\tMax: %s" % maximum)
# command = input("Waiting before exiting")

print('Done')

