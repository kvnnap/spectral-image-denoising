# recomputes all run scores using a different image loader. Needed for colour experiments

import sys
import os
import argparse
import time
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import MetricFactory
from evaluation.thresholds import ThresholdFactory


from evaluation.denoiser_factory import DenoiserFactory
from utils.image import alpha_correction_chain, save_image_as_png, save_image_as_exr, set_base_path, tone_map, tone_map_aces
from utils.versioning import get_version
from utils.serialisation import load, save_text
from utils.string import comma_to_list, get_mapped_scene_name, tables_to_csv
from utils.serialisation import save, load
from visualisation.result_image_processor import ResultImageProcessor


def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Generate image from coeffs in results.\n{versionString}')
    # smb/exp_1c/runs_merged.json
    parser.add_argument('--result', default='', help='The original result to load')
    parser.add_argument('--image-base', default='seeded-images', help='Base path for the images to load (Seeded-images)')
    parser.add_argument('--pre-image-loader', default='rgb_aces_tm_nogamma', help='Leave blank to use original one from result. Would recompute same scores.')
    parser.add_argument('--out-result', default='', help='A new json with scores replaced')
    args = parser.parse_args()
    set_base_path(args.image_base)

    print(f'Loading {args.result}')

    runData = load(args.result)

    imageLoader = ImageLoaderFactory.create(args.pre_image_loader)

    for i, run in enumerate(runData.runs):
        print(f'\rProgress {i + 1}/{len(runData.runs)}', end='', flush=True)
        # rip = ResultImageProcessor(run)

        # Clear to save space
        run.denoiserResult.func_vals = []
        run.denoiserResult.x_iters = []
        del run.bestMetricResults

        dp = run.denoiserParams

        # Fill this so that add_all_metrics.py works (best metrics additions)
        dp.imageLoader = args.pre_image_loader

        # Get score
        ref, noisy = imageLoader(dp.pairImage[0]), imageLoader(dp.pairImage[1])
        denoiserMethod = DenoiserFactory.create(dp.denoiser)
        thresholdMethod = ThresholdFactory.create(dp.thresholding)
        den = denoiserMethod.get_image(noisy, run.denoiserResult.x, thresholdMethod)

        metricMethod = MetricFactory.create(dp.metric)

        # New score
        run.denoiserResult.fun = metricMethod(ref, den, dp)

    runData.version = get_version().to_dict()
    runData.cores = -1
        
    save(args.out_result, runData)

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()