import sys
import os
import argparse
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import save, load
from utils.image import set_base_path, load_image

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Fix MSE score.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='Result to fix')
    parser.add_argument('--fixed-result', default='fixed_mse_result.json', help='File path to fixed result')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    args = parser.parse_args()

    set_base_path(args.image_base)

    resultPath = args.result
    fixedResultPath = args.fixed_result

    fixCount = 0
    runData = load(resultPath)
    imgDict = {}
    for run in runData.runs:
        dp = run.denoiserParams
        if dp.metric != 'mse':
            continue
        fixCount += 1
        # Load image to get shape
        imagePath = dp.pairImage[0]
        if imagePath not in imgDict:
            imgDict[imagePath] = (1.0 / np.prod(load_image(imagePath).shape)).item()
        shapeDimReciprocal = imgDict[imagePath]
        
        dr = run.denoiserResult
        dr.fun *= shapeDimReciprocal
        for i in range(len(dr.func_vals)):
            dr.func_vals[i] *= shapeDimReciprocal

    runData.version = get_version().to_dict()
    runData.cores = -1
    
    save(fixedResultPath, runData)
    save(f'{fixedResultPath}.norefs.json', runData, False)

    print(f'Fixed the mse of {fixCount} results')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

