from utils.image import *
from evaluation.metric import *
import copy
import time
import gc

import matlab
import hdrpy

from pympler import muppy, summary, tracker

# try:
h = hdrpy.initialize()

# 24 inch Full HD display, observed from 30cm distance
ppd = h.hdrvdp_pix_per_deg(24.0, matlab.double([1920, 1080]), 0.30)

ref = load_image('smb/images/povray_reflect_caustics_8.exr', True, False)
noisy = load_image('smb/images/povray_reflect_caustics_2.exr', True, False)

selector = { 
    'gray': 'luminance', 
    'gray_tm': 'luma-display',
    'gray_aces_tm': 'luma-display',
    'rgb': 'rgb-native',
    'rgb_tm': 'sRGB-display',
    'rgb_aces_tm': 'sRGB-display'
}
s = selector['gray']

times = []
#tr = tracker.SummaryTracker()
for i in range(200):
    noisy = np.ascontiguousarray(copy.deepcopy(noisy))
    ref = np.ascontiguousarray(copy.deepcopy(ref))
    noisyP = matlab.single(noisy)
    refP = matlab.single(ref)
    start = time.perf_counter_ns()
    result = h.hdrvdp3('side-by-side', noisyP, refP, s, ppd, ['quiet', True])
    #tr.print_diff()
    finish = time.perf_counter_ns()
    times.append((finish - start) * 1e-6)

#summary.print_(summary.summarize(muppy.get_objects()))


# command = input("Waiting before unloading h")

# h.terminate()
# del h
# gc.collect()

# command = input("Waiting before unloading h")

# hdrpy.terminate_runtime()
# gc.collect()

command = input("Waiting before exiting")

print('Done')

