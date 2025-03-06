# list all directories in the results directory, using pathlib
# Each directory name is the scene name, e.g., 'scene_01', 'scene_02'
# Each child directory contains the scene camera used to render the image
# Each grandchild directory contains shader name used to render  the image
# Each file in the grandchild directory is an image rendered by the scene camera and shader,
# at specific samples per pixel rates. 
# The example directory structure would look like:
# Results/scene_01/camera_01/shader_01/image_shader_01_buffer_name_0.exr

# Example: veach-bidir/Camera.001/lt/veach_bidir_lt_rad_acc_7.exr

import sys
import os
import argparse
import re
import tqdm
import matplotlib.pyplot as plt

from pathlib import Path
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import *
from utils.serialisation import load, save, save_text
from utils.image import set_base_path
from utils.string import comma_to_list

# Globals

# imageBufferTypes = ["diff_acc", "spec_acc", "caus_acc", "rad_acc"]
imageLoaderStr = None
imageLoader = None
file_pattern = None
shader_pattern = None
metric_pattern = None
buffer_pattern = None

ref_name = 'ref'
ref_pattern = fr"^({ref_name})$"

metric_fns = {
    'flip':      lambda ref, noisy, dp :  local_flip(ref, noisy, dp),
    'hdrvdp3':   lambda ref, noisy, dp : -local_hdrvdp3(ref, noisy, dp),
    'mse':       lambda ref, noisy, dp :  local_mse(ref, noisy, dp),
    'psnr':      lambda ref, noisy, dp : -local_psnr(ref, noisy, dp),
    'ssim':      lambda ref, noisy, dp : -local_ssim(ref, noisy, dp),
}

class DPString:
    def __init__(self, imageLoader):
        self.imageLoader = imageLoader

def compute_score(ref, noisy, imgLoaderStr):
    dp = DPString(imgLoaderStr)
    ret_obj = {}
    for metric_name, similarity_fn in metric_fns.items():
        ret_obj[metric_name] = similarity_fn(ref, noisy, dp)
    return ret_obj

def compare_images(ref_data, noisy_image):
    noisy_data = imageLoader(noisy_image['image'])
    score = compute_score(ref_data, noisy_data, imageLoaderStr)
    return score

# Get list of directories in the results directory using pathlib
def scan_directory(results_dir):
    image_counter = 0
    g_image_map = defaultdict(dict)
    for scene in results_dir.iterdir():
        if not scene.is_dir():
            continue
        for camera in scene.iterdir():
            if not camera.is_dir():
                continue
            my_images = []
            for shader in camera.iterdir():
                if not shader.is_dir() or not re.match(shader_pattern, shader.name):
                    continue

                # Get list of all exr files in each shader directory using pathlib
                for image in shader.iterdir():
                    if not image.is_file():
                        continue
                    match = re.match(file_pattern, image.name)
                    if not match:
                        continue
                    if match.group('extension').lower() != 'exr':
                        continue

                    # Concat image object with match.groupdict()
                    my_image = { 'image': str(image.relative_to(results_dir)) }
                    # my_image = {'image': image }
                    my_image.update(match.groupdict())
                    my_image['sequence_number'] = int(match.group('sequence_number'))
                    my_images.append(my_image)
                    if ref_name != shader.name:
                        image_counter += 1

            # Generate map of images by buffer type and shader type
            my_images.sort(key=lambda x: x['sequence_number'])
            image_map = defaultdict(lambda: defaultdict(list))
            for image in my_images:
                image_map[image['buffer_type']][image['shader']].append(image)
            if image_map:
                g_image_map[scene.name][camera.name] = image_map
    return (g_image_map, image_counter)

def compute_scores(g_image_map, image_counter):
    # Create a progress bar to track the progress of processing each buffer type and shader type
    bar = tqdm.tqdm(total=image_counter, desc="Computing Scores")
    for scene, cameras in g_image_map.items():
        for camera, image_map in cameras.items():
            for buff_type, shaders_image_map in image_map.items():
                # Grab the last image and use as reference for comparison
                if ref_name not in shaders_image_map:
                    continue
                images = shaders_image_map[ref_name]
                if not images:
                    continue

                ref_image = images[-1]
                ref_data = imageLoader(ref_image['image'])

                for shader, img_list in shaders_image_map.items():
                    if shader == ref_name:
                        continue  # Skip the reference shader
                    
                    # The rest of the images are compared to the reference image
                    for img in img_list:
                        img['score'] = compare_images(ref_data, img)
                        bar.update(1)
    bar.close()

def plot_scores(g_image_map, out_dir):
    # plots_dir = Path(out_dir).joinpath(f'{scene}/{camera}')
    plots_dir = Path(out_dir)

    # Get number of plots for progress bar
    num_plots = 0
    for scene, cameras in g_image_map.items():
        for camera, image_map in cameras.items():
            for buff_type, shaders_image_map in image_map.items():
                if not re.match(buffer_pattern, buff_type):
                    continue
                metrics = set()
                for shader, images in shaders_image_map.items():
                    if not re.match(shader_pattern, shader):
                        continue
                    for img in images:
                        if 'score' not in img: continue
                        for metric, score in img['score'].items():
                            if re.match(metric_pattern, metric):
                                metrics.add(metric)
                num_plots += len(metrics)

    plt.ioff()
    bar = tqdm.tqdm(total=num_plots, desc="Plotting Scores")
    for scene, cameras in g_image_map.items():
        for camera, image_map in cameras.items():
            specific_dir = plots_dir.joinpath(f'{scene}-{camera}')
            specific_dir.mkdir(parents=True, exist_ok=True)
            for buff_type, shaders_image_map in image_map.items():
                if not re.match(buffer_pattern, buff_type):
                    continue
                # Get Scores for this scene, camera, and buffer type
                seqs = defaultdict(list)
                scores = defaultdict(lambda: defaultdict(list))
                for shader, images in shaders_image_map.items():
                    if not re.match(shader_pattern, shader):
                        continue
                    for img in images:
                        if 'score' not in img:
                            continue  # Skip images without scores
                        seqs[shader].append(img['sequence_number'])
                        for metric, score in img['score'].items():
                            if re.match(metric_pattern, metric):
                                scores[metric][shader].append(score)
                
                # Plot data for each metric, one plot per metric
                for metric, shaders in scores.items():
                    plt.figure(figsize=(10, 6))
                    plt.title(f'{scene} - {camera} - {buff_type} [{imageLoaderStr}]')
                    # plt.text(0.95, 0.05, f'{scene} - {camera} - {buff_type}',
                    #          horizontalalignment='right', verticalalignment='bottom',
                    #          transform=plt.gca().transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
                    plt.xlabel('Samples (4^x)')
                    plt.ylabel(metric.upper())  # Metric name as y-axis label
                    for shader, scores in shaders.items():
                        x = seqs[shader] # x = range(len(scores))
                        y = scores
                        plt.plot(x, y, marker='o', linestyle='-', label=shader)
                    plt.legend()
                    plt.savefig(specific_dir.joinpath(f'{scene}_{camera}_{buff_type}_{metric}_plot.png'))
                    plt.close()
                    bar.update(1)
    bar.close()
    plt.ion()

    # Set x-axis ticks to show 4^index
    # plt.xticks(x, [f'4^{i}' for i in x])

def main():
    parser = argparse.ArgumentParser(description=f'Compare images and generate plots for each scene, camera, buffer type and metric combination.')
    parser.add_argument('--results-dir', type=str, required=True, help='Path to the Results directory containing images for comparison.')
    parser.add_argument('--output-dir', type=str, default='plots', help='Directory to save the output plot and scores to.')
    parser.add_argument('--image-loader', type=str, default='rgb_aces_tm_nogamma', help='Which loader to use when loading EXR images.')
    parser.add_argument('--scores-file', type=str, default='scores.json', help='Name of the scores JSON file to load/save.')
    parser.add_argument('--plot-only', action='store_true', help='If set, only plot the graph without recomputing scores.')
    # List-based
    parser.add_argument('--metrics', default='flip,hdrvdp3,mse,psnr,ssim', help='The metric name to use for comparison. Default all metrics.')
    parser.add_argument('--buffer-types', default='diff_acc,spec_acc,caus_acc,rad_acc', help='The buffer types to use for comparison. Defaults to all buffer types.')
    parser.add_argument('--shaders', default='pt,lt,lt_opt,lt_imp_dist,lt_imp_dist_cam,lt_imp_dist_cam_rt', help='The shaders to use for comparison. Defaults to all shaders.')

    args = parser.parse_args()

    global imageLoaderStr, imageLoader, file_pattern, shader_pattern, metric_pattern, buffer_pattern, metric_fns
    imageLoaderStr = args.image_loader
    imageLoader = ImageLoaderFactory.create(imageLoaderStr)

    metrics = comma_to_list(args.metrics)
    buffer_types = comma_to_list(args.buffer_types)
    shaders = comma_to_list(args.shaders)

    if not(metrics and buffer_types and shaders):
        print("Please specify at least one buffer type, shader, and metric.")
        parser.print_help()
        return

    file_pattern = fr"^(?P<name>.*)_(?P<shader>{'|'.join(shaders)}|ref)_(?P<buffer_type>{'|'.join(buffer_types)})_(?P<sequence_number>\d+)(?:\.(?P<extension>\w+))?$"
    shader_pattern = fr"^({'|'.join(shaders)}|ref)$"
    buffer_pattern = fr"^({'|'.join(buffer_types)})$"
    metric_pattern = fr"^({'|'.join(metrics)})$"
    
    # Remove all metric functions not matching the metric_pattern
    metric_fns = {metric: metric_fn for metric, metric_fn in metric_fns.items() if re.match(metric_pattern, metric) }

    results_dir = Path(args.results_dir)
    output_dir  = Path(args.output_dir)
    scores_file  = output_dir / Path(args.scores_file)

    set_base_path(str(results_dir)) # This is a global

    if args.plot_only:
        g_image_map = load(scores_file)
    else:
        g_image_map, image_counter = scan_directory(results_dir)
        compute_scores(g_image_map, image_counter)
        save(scores_file, g_image_map)

    plot_scores(g_image_map, output_dir)

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()
