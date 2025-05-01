import sys
import os
import argparse
import numpy as np

from pathlib import Path
from matplotlib import pyplot as plt
from matplotlib import ticker as ticker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load, save
from utils.image import set_base_path
from visualisation.result_image_processor import ResultImageProcessor

def get_run_from__run_id(runData, runId):
    return next((x for x in runData.runs if x.denoiserParams.id == runId), None)

def get_score(resImageProc, ref, noisy):
    resImageProc.update_image(noisy)
    resImageProc.update_ref_image(ref)
    return resImageProc.compute_score()

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Try varying transformations on input image.\n{versionString}')
    parser.add_argument('--result', default='', help='Result file to load')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    parser.add_argument('--out-scores', default='image_trans_scores.json', help='Scores json')
    parser.add_argument('--run-id', default=0, type=int, help='The run id to run tests on')
    args = parser.parse_args()

    set_base_path(args.image_base)

    # If file args.out_scores exists (using pathlib)
    out_path = Path(args.out_scores)
    if out_path.exists():
        print(f'Found existing {args.out_scores} file. Loading scores directly')
        scores = load(args.out_scores)
    else:
        print(f'Loading result {args.result} and computing scores to {args.out_scores}.. This might take a while')
        runData = load(args.result)
        run = get_run_from__run_id(runData, args.run_id)
        resImageProc = ResultImageProcessor(run)

        # Translation tests - y and x divs
        divs = (10, 10, 1)
        origNoisy = resImageProc.image
        origRefImage = resImageProc.refImage
        steps = tuple(x // y for x, y in zip(origNoisy.shape, divs))

        ops=[
            ('Identity', lambda x: x),
            ('FlipLR', lambda x: np.fliplr(x)),
            ('FlipUD', lambda x: np.flipud(x))
        ]

        # tScore (op, hor/ver, score)
        scores={}
        for op in ops:
            noisy = op[1](origNoisy)
            ref = op[1](origRefImage)

            tScore = {'Hor': [], 'Ver': [] }
            for i, orientation in enumerate(['Hor', 'Ver']):
                for _ in range(divs[i]):
                    score = get_score(resImageProc, ref, noisy)
                    tScore[orientation].append(score)
                    noisy = np.roll(noisy, steps[i], axis=i)
                    ref = np.roll(ref, steps[i], axis=i)
            scores[op[0]] = tScore

        save(args.out_scores, scores)
        print(f'Saved scores to {args.out_scores}')

    # Define transformation types
    transformations = ['Identity', 'FlipLR', 'FlipUD']

    # Define metrics
    metrics = ['flip', 'mse', 'ssim', 'psnr', 'hdrvdp3']

    # Define colors for plotting
    colors = ['b', 'g', 'r', 'c']

    # Create subplots in a 2x2 grid
    plt.ioff()
    fig, axs = plt.subplots(3, 2, figsize=(12, 10))
    fig.delaxes(axs[2, 1])

    textSize = 18
    tickSize = 14

    handles = []
    labels = []

    # Iterate over metrics
    for i, metric in enumerate(metrics):
        # Calculate subplot position
        row = i // 2
        col = i % 2

        ax = axs[row, col]
        
        # Plot metric scores for each transformation type
        for j, trans in enumerate(transformations):
            # Extract scores for reference and denoised images
            noisy_hor_scores = np.array([scores[trans]['Hor'][k][metric][0] for k in range(len(scores[trans]['Hor']))])
            noisy_ver_scores = np.array([scores[trans]['Ver'][k][metric][0] for k in range(len(scores[trans]['Ver']))])
            den_hor_scores = np.array([scores[trans]['Hor'][k][metric][1] for k in range(len(scores[trans]['Hor']))])
            den_ver_scores = np.array([scores[trans]['Ver'][k][metric][1] for k in range(len(scores[trans]['Ver']))])
            
            if metric in ['mse', 'flip']:
                hor_scores = noisy_hor_scores / den_hor_scores
                ver_scores = noisy_ver_scores / den_ver_scores
            else:
                hor_scores = den_hor_scores / noisy_hor_scores
                ver_scores = den_ver_scores / noisy_ver_scores

            # Plot reference and denoised scores
            l_hor, l_ver = (f'Horizontal {trans}', f'Vertical {trans}')
            line_hor, = ax.plot(hor_scores, label=l_hor, linestyle='--', color=colors[j])
            line_ver, = ax.plot(ver_scores, label=l_ver, linestyle='-',  color=colors[j])
            ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))

            # Store handles and labels for the legend (only once)
            if i == 0:
                handles.append(line_hor)
                handles.append(line_ver)
                labels.append(l_hor)
                labels.append(l_ver)
        
        # Add labels and legend
        ax.set_xlabel('Increment', fontsize=textSize)
        ax.set_ylabel(metric.upper() + ' score ratio', fontsize=textSize)
        # ax.set_title(metric.upper() + ' Scores for Different Transformations', fontsize=textSize)
        ax.tick_params(axis='both', labelsize=tickSize)
        # ax.legend()

    fig.legend(handles, labels, loc='center', bbox_to_anchor=(0.75, 0.2), fontsize=textSize)

    # Adjust layout
    plt.tight_layout()

    # Show plots
    # plt.show()

    plt.savefig(out_path.with_suffix('.png'))

    

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()
