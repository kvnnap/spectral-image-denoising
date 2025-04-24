import glob
import sys
import os
import argparse
import time
from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib import ticker as ticker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image import alpha_correction_chain, save_image_as_png, save_image_as_exr, set_base_path, tone_map, tone_map_aces
from utils.versioning import get_version
from utils.serialisation import load, save
from utils.string import comma_to_list, get_scene_name
from visualisation.result_image_processor import ResultImageProcessor

def find_exr_files(directory="."):
    exr_files = glob.glob(os.path.join(directory, "*.exr"))
    return sorted(exr_files)

def pair_filenames(filenames):
    # Dictionary to hold lists of filenames indexed by the common suffix (without extension)
    grouped_filenames = {}

    for filename in filenames:
        # Remove the extension and split the filename into parts
        base_name = filename.rsplit('.', 1)[0]
        parts = base_name.split('_')
        if len(parts) < 4:
            continue

        # Extract the variable parts of the filename
        prefix = '_'.join(parts[:2])  # 'caustic_glass'
        middle_number = parts[2]      # Either '2' or '8'
        suffix = '_'.join(parts[3:])  # 'caustics_x'

        # Use the suffix as a grouping key
        if suffix not in grouped_filenames:
            grouped_filenames[suffix] = {'2': None, '8': None}

        if middle_number in grouped_filenames[suffix]:
            grouped_filenames[suffix][middle_number] = filename

    # Create a list of dictionaries to store the pair details
    paired_objects = []

    # A helper function to extract the number after 'caustics_'
    def extract_suffix_number(suffix):
        return int(suffix.split('_')[-1])

    for suffix, group in grouped_filenames.items():
        file1 = group['2']
        file2 = group['8']
        if file1 and file2:
            paired_objects.append({
                'num': extract_suffix_number(suffix),
                'noisy': file1,
                'reference': file2
            })

    # Sort paired objects by the 'num' field
    paired_objects.sort(key=lambda obj: obj['num'])

    return paired_objects

class PlotComparison:
    def __init__(self, paired_objects, scores, metric_name):
        """
        Initializes the PlotComparison object with data and parameters.

        :param paired_objects: List of dictionaries. Each dictionary contains {'num': <sequence number>, 'noisy': <filename>, 'reference': <filename>}
        :param scores: List of tuples, where each tuple contains multiple numeric scores for the same pair.
        :param metric_name: Name of the metric for labeling the y-axis.
        """
        self.paired_objects = paired_objects
        self.scores = scores
        self.metric_name = metric_name

    def plot(self):
        """
        Plots the comparison scores against the sequence numbers.
        """
        sequence_numbers = [obj['num'] + 1 for obj in self.paired_objects]
        
        # Check consistency
        if len(sequence_numbers) != len(self.scores):
            raise ValueError("The length of sequence numbers and scores must match.")

        # Determine the number of score components in each tuple
        num_components = len(self.scores[0])

        # Create a separate list for each component of the scores
        component_scores = [[] for _ in range(num_components)]
        for score_tuple in self.scores:
            for i, score in enumerate(score_tuple):
                component_scores[i].append(score)

        # Plotting
        plt.figure(figsize=(12, 8))  # Increase the figure size for better readability

        # Plot each component with a different color/line style
        text = ['Noisy-Ref', 'Denoised-Ref']
        for i in range(num_components):
            plt.plot(
                sequence_numbers,
                component_scores[i],
                marker='o',
                linestyle='-',
                label=f'{text[i] if i < len(text) else "Score " + str(i)}'
            )

        textSize = 16
        tickSize = 12

        # Setting font size for title, labels, and ticks
        plt.title('Noisy and Denoised Animation Score', fontsize=textSize)
        plt.xlabel('Frame Number', fontsize=textSize)
        plt.ylabel(f'{self.metric_name.upper()} Score', fontsize=textSize)
        plt.xticks(fontsize=tickSize)
        plt.yticks(fontsize=tickSize)

        # Format Y-axis numbers in scientific notation
        ax = plt.gca()
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        # Set font size for the scientific notation text
        ax.yaxis.get_offset_text().set_size(tickSize)  # Set the font size for the offset text

        # Optional: Adding grid and legend
        plt.grid(True)
        plt.legend(loc='best', fontsize=textSize)  # Use 'best' to automatically place the legend

        # Show the plot
        plt.tight_layout()  # Adjust layout to prevent clipping

        def on_resize(event):
            plt.tight_layout()
        plt.gcf().canvas.mpl_connect('resize_event', on_resize)

        plt.show()

def main():
    # Uncomment below if json file already generated
    # myPlt = load("myPlt.json")
    # myPlt.plot()
    # return

    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Generate image from coeffs in results.\n{versionString}')
    # smb/exp_1c/runs_merged.json
    parser.add_argument('--result', default='', help='The result to load')
    parser.add_argument('--run-id', default=0, type=int, help='The run id to load coeffs from')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    parser.add_argument('--image', default='', help='Path to image or dir. If empty, will grab all exr images in current directory.')


    parser.add_argument('--pre-image-loader', default='', help='Leave blank to use original one from result')
    parser.add_argument('--post-procs', default='', help='Comma separated aces_tm,tm,gamma')
    parser.add_argument('--formats', default='exr', help='Comma separated exr,png')
    parser.add_argument('--out-dir', default='', help='Directory where to save images')
    args = parser.parse_args()
    set_base_path(args.image_base)

    formatMap = {
        'exr': lambda x, y: save_image_as_exr(x, f'{y}.exr'),
        'png': lambda x, y: save_image_as_png(x, f'{y}.png')
    }

    ppMap = {
        'aces_tm': tone_map_aces,
        'tm': tone_map,
        'gamma': alpha_correction_chain,
    }
    
    # process input
    formats = comma_to_list(args.formats)
    postProc = comma_to_list(args.post_procs)

    # Validate
    for format in formats:
        if format not in formatMap.keys():
            print(f"Wrong format {format}")
            return
    
    for pp in postProc:
        if pp not in ppMap.keys():
            print(f"Wrong post-proc {format}")
            return
        
    pImage = Path(args.image)
    if args.image and pImage.is_file() and pImage.suffix.strip().lower() == '.exr':
        images = [ args.image ]
    else:
        images = find_exr_files(args.image)
    
    pairedImages = pair_filenames(images)

    descString = f'Loading {args.result} '
    descString += f'applying {args.pre_image_loader if args.pre_image_loader else "default"} pre-image loader '
    descString += f'applying {",".join(postProc) if postProc else "no"} post-processing step(s) '
    descString += f'and saving images to {args.out_dir}'
    print(descString)

    runData = load(args.result)
    run = runData.runs[args.run_id]

    rip = ResultImageProcessor(run)

    # alter image loader to apply coeffs on
    if args.pre_image_loader:
        rip.update_image_loader(args.pre_image_loader)

    # Gen filename
    dp = run.denoiserParams
    sceneName = get_scene_name(dp.pairImage[0])

    # Gen scores and possibly save images
    set_base_path('')
    scores = []
    metricName = dp.metric
    for imagePath in pairedImages:
        # get noisy
        rip.update_ref_image_path(imagePath['reference'])
        rip.update_image_path(imagePath['noisy'])
        (_, den, _) = rip.get(False)
        allScores = rip.compute_score()
        scoreWithRunMetric = allScores[metricName]
        scores.append(scoreWithRunMetric)
        
        # Save denoised images
        # Post proc
        for pp in postProc:
            den = ppMap[pp](den)

        # save
        fileName = f'{sceneName}_{dp.metric}_{dp.id}_den_{imagePath["num"]}'
        destFilePath = str(Path(args.out_dir).joinpath(fileName))
        for format in formats:
            formatMap[format](den, destFilePath)

    # Save all parameters

    myPlt = PlotComparison(pairedImages, scores, metricName)
    save("myPlt.json", myPlt)

    myPlt.plot()

    print('\nCompleted')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()
    # myPlt = load("myPlt.json")
    # myPlt.plot()

