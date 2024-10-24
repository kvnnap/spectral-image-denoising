import sys
import os
import argparse


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import CONV
from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import MetricFactory
from utils.versioning import get_version
from utils.string import array_to_latex_table, comma_to_list

class DPString:
    def __init__(self, imageLoader):
        self.imageLoader = imageLoader

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Generate image from coeffs in results.\n{versionString}')
    # smb/exp_1c/runs_merged.json
    parser.add_argument('--images', default='', help='The result to load')
    parser.add_argument('--metrics', default='', help='The metric name to use for comparison')
    parser.add_argument('--image-loaders', default='rgb,rgb_aces_tm_nogamma', help='Leave blank to use original one from result')
    args = parser.parse_args()

    # process input
    images = comma_to_list(args.images)
    metrics = comma_to_list(args.metrics)
    imageLoaders = comma_to_list(args.image_loaders)

    descString = f'Loading {",".join(images)}, '
    descString += f'applying {args.image_loaders} pre-image loader '
    descString += f' and comparing using  {",".join(metrics)} metrics'
    print(descString)

    # Load images
    loaders = [(x, ImageLoaderFactory.create(x)) for x in imageLoaders]
    loadedImages = {l[0]: [l[1](image) for image in images] for l in loaders}

    results_table = [["Metric", "Score", "Score TM"]]

    # Load metrics and compute comparison
    for m in metrics:
        metric = MetricFactory.create(m)
        n = len(images)
        for i in range(n):
            for j in range(i+1, n):
                res = [m]
                for il in imageLoaders:
                    computed = metric(loadedImages[il][i], loadedImages[il][j], DPString(il))
                    res.append(CONV[m](computed))
                results_table.append(res)

    # Help, need to convet the results to a latex table
    latex_table = array_to_latex_table(results_table)
    print(latex_table)
    

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()