import sys
import os
import argparse
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/evaluation')

from evaluation.denoiser_factory import DenoiserFactory
from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import MetricFactory
from evaluation.thresholds import ThresholdFactory

from utils.versioning import get_version
from utils.serialisation import save, load, print_obj

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Visualises results produced by evaluation/run.py.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='Where to load the JSON RunData object from')
    args = parser.parse_args()

    resultPath = args.result

    runData = load(resultPath)

    firstRun = runData.runs[0]
    dp = firstRun.denoiserParams

    pairImage = dp.pairImage
    iteration = dp.iterations
    imageLoaderMethod = ImageLoaderFactory.create(dp.imageLoader)
    metricMethod = MetricFactory.create(dp.metric)
    thresholdMethod = ThresholdFactory.create(dp.thresholding)
    denoiserMethod = DenoiserFactory.create(dp.denoiser)

    
    pass

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()