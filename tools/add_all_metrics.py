import sys
import os
import argparse
import multiprocessing as mp
from functools import partial

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.array import split_partition_array
from utils.versioning import get_version
from utils.serialisation import save, load
from utils.image import set_base_path
from evaluation.image_loader import ImageLoaderFactory
from evaluation.thresholds import ThresholdFactory
from evaluation.denoiser_factory import DenoiserFactory
from evaluation.metric import *

def task(runs, imageBase):
    set_base_path(imageBase)

    imgDict = {}
    scoreDict = {}
    metrics = { 'flip': local_flip, 'hdrvdp3': local_hdrvdp3, 'mse': local_mse, 'psnr': local_psnr, 'ssim': local_ssim }
    result = []
    for run in runs:
        dp = run.denoiserParams

        # Load images if not in dictionary
        imgs = []
        for img in dp.pairImage:
            imageDictEntry = img + '-' + dp.imageLoader
            if imageDictEntry not in imgDict:
                imageLoaderMethod = ImageLoaderFactory.create(dp.imageLoader)
                imgDict[imageDictEntry] = imageLoaderMethod(img)
            # Get image reference
            imgs.append(imgDict[imageDictEntry])

        # Get score
        ref, noisy = (imgs[0], imgs[1])
        denoiserMethod = DenoiserFactory.create(dp.denoiser)
        thresholdMethod = ThresholdFactory.create(dp.thresholding)
        coeffs = run.denoiserResult.x
        den = denoiserMethod.get_image(noisy, coeffs, thresholdMethod)

        # Fill scoreDict
        scoreDictEntry =  '-'.join(dp.pairImage) + '-' + dp.imageLoader
        if scoreDictEntry not in scoreDict:
            scoreDict[scoreDictEntry] = {k: v(ref, noisy, dp) for k,v in metrics.items()}
        result.append({k: (scoreDict[scoreDictEntry][k], v(ref, den, dp)) for k,v in metrics.items()})
    return result

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Add all metrics to result.\n{versionString}')
    parser.add_argument('--result', default='all_results.json', help='Result to load')
    parser.add_argument('--image-base', default='smb/images', help='Base path for the images to load')
    parser.add_argument('--output-result', default='all_metric_results.json', help='Output filename for results + metrics')
    parser.add_argument('--cores', default=0, type=int, help='Number of cores to use. 0 uses maximum')
    args = parser.parse_args()

    resultPath = args.result
    outputResultPath = args.output_result
    cores = args.cores if args.cores > 0 and args.cores <= mp.cpu_count() else mp.cpu_count()

    print('Loading result')
    runData = load(resultPath)

    print('Processing')
    boundTask = partial(task, imageBase=args.image_base)
    splitRuns = [split_partition_array(runData.runs, cores, i, 1) for i in range(cores)]
    if cores == 1:
        # pResults = [boundTask(runData.runs)]
        pResults = map(boundTask, splitRuns)
    else:
        with mp.Pool(processes=cores, maxtasksperchild=1) as pool:
            pResults = pool.map(boundTask, splitRuns)
            pool.close()
            pool.join()

    it = (run for runs in pResults for run in runs)
    for run in runData.runs:
        run.bestMetricResults = next(it)

    runData.version = get_version().to_dict()
    runData.cores = -1
    
    print('Saving')
    save(outputResultPath, runData)

    print(f'Done adding metrics')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    mp.set_start_method('spawn')
    main()

