import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load
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
    parser.add_argument('--result', default='results/paper_exp_1_gray-result_clip.json', help='Result file to load')
    parser.add_argument('--image-base', default='images/exp_1', help='Base path for the images to load')
    parser.add_argument('--run-id', default=0, type=int, help='The run id to run tests on')
    args = parser.parse_args()

    set_base_path(args.image_base)

    resultPath = args.result
    runId = args.run_id
    runData = load(resultPath)

    run = get_run_from__run_id(runData, runId)
    resImageProc = ResultImageProcessor(run)

    # Translation tests - y and x divs
    divs = (8, 8, 1)
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
        
        resImageProc.image = op[1](origNoisy)
        resImageProc.refImage = op[1](origRefImage)
        tScore = {'Hor': [], 'Ver': [] }

        for i, orientation in enumerate(['Hor', 'Ver']):
            for _ in range(divs[i]):
                noisy = np.roll(resImageProc.image, steps[i], axis=i)
                ref = np.roll(resImageProc.refImage, steps[i], axis=i)
                score = get_score(resImageProc, ref, noisy)
                tScore[orientation].append(score)
        scores[op[0]] = tScore
        

    resImageProc.update_image(origNoisy)
    resImageProc.update_ref_image(origRefImage)



    # Define transformation types
    transformations = ['Identity', 'FlipLR', 'FlipUD']

    # Define metrics
    metrics = ['mse', 'ssim', 'psnr', 'hdrvdp3']

    # Define colors for plotting
    colors = ['b', 'g', 'r', 'c']

    # Create subplots in a 2x2 grid
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    # Iterate over metrics
    for i, metric in enumerate(metrics):
        # Calculate subplot position
        row = i // 2
        col = i % 2
        
        # Plot metric scores for each transformation type
        for j, transformation in enumerate(transformations):
            # Extract scores for reference and denoised images
            noisy_hor_scores = np.array([scores[transformation]['Hor'][k][metric][0] for k in range(len(scores[transformation]['Hor']))])
            noisy_ver_scores = np.array([scores[transformation]['Ver'][k][metric][0] for k in range(len(scores[transformation]['Ver']))])
            den_hor_scores = np.array([scores[transformation]['Hor'][k][metric][1] for k in range(len(scores[transformation]['Hor']))])
            den_ver_scores = np.array([scores[transformation]['Ver'][k][metric][1] for k in range(len(scores[transformation]['Ver']))])
            
            hor_scores = den_hor_scores - noisy_hor_scores
            ver_scores = den_ver_scores - noisy_ver_scores

            # Plot reference and denoised scores
            axs[row, col].plot(hor_scores, label='Den-H ' + transformation, linestyle='--', color=colors[j])
            axs[row, col].plot(ver_scores, label='Den-V' + transformation, linestyle='-', color=colors[j])
        
        # Add labels and legend
        axs[row, col].set_xlabel('Sample')
        axs[row, col].set_ylabel(metric.upper() + ' Score')
        axs[row, col].set_title(metric.upper() + ' Scores for Different Transformations')
        axs[row, col].legend()

    # Adjust layout
    plt.tight_layout()

    # Show plots
    plt.show()


    pass
    # Translation + Flip tests
    

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

