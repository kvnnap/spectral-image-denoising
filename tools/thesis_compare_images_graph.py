# list all directories in the results directory, using pathlib
# Each directory name is the scene name, e.g., 'scene_01', 'scene_02'
# Each child directory contains the scene camera used to render the image
# Each grandchild directory contains shader name used to render  the image
# Each file in the grandchild directory is an image rendered by the scene camera and shader,
# at specific samples per pixel rates. 
# The example directory structure would look like:
# Results/scene_01/camera_01/shader_01/image_shader_01_buffer_name_0.exr

# Example: veach-bidir/Camera.001/lt/veach_bidir_lt_rad_acc_7.exr

import multiprocessing
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')

import sys
import os
import argparse
import re
import tqdm
import matplotlib.pyplot as plt

from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import *
from utils.serialisation import load, save
from utils.image import save_image_as_exr, save_image_as_png, set_base_path, get_base_path
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
    'lpips':     lambda ref, noisy, dp :  local_lpips(ref, noisy, dp),
}

class DPString:
    def __init__(self, imageLoader):
        self.imageLoader = imageLoader

def get_config(config, scene, camera):
    ret_conf = {} | config.get("global", {})
    ret_conf = ret_conf | config.get("local", {}).get(scene, {}).get(camera, {})
    return None if len(ret_conf) == 0 else ret_conf

def compute_score(ref, noisy, imgLoaderStr, metrFns):
    dp = DPString(imgLoaderStr)
    ret_obj = {}
    for metric_name, similarity_fn in metrFns.items():
        try:
            ret_obj[metric_name] = similarity_fn(ref, noisy, dp)
        except Exception as e:
            ret_obj[metric_name] = None
    return ret_obj

# Get list of directories in the results directory using pathlib
def scan_directory(results_dir):
    image_counter = 0
    g_image_map = defaultdict(dict)
    for scene in sorted(results_dir.iterdir()):
        if not scene.is_dir():
            continue
        for camera in sorted(scene.iterdir()):
            if not camera.is_dir():
                continue
            my_images = []
            for shader in sorted(camera.iterdir()):
                if not shader.is_dir() or not re.match(shader_pattern, shader.name):
                    continue

                # Get list of all exr files in each shader directory using pathlib
                for image in sorted(shader.iterdir()):
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

def generate_images(g_image_map, config, output_dir):
    png = True
    if config is None:
        return
    trans_dir = output_dir / 'extra'
    imageLoader = ImageLoaderFactory.create('rgb_aces_tm' if png else 'rgb')
    for scene, cameras in g_image_map.items():
        for camera, image_map in cameras.items():
            local_config = get_config(config, scene, camera)
            if local_config is None:
                continue
            for buff_type, shaders_image_map in image_map.items():
                for shader, img_list in shaders_image_map.items():
                    for img in img_list:
                        transformed_image = imageLoader(img['image'], local_config)
                        transformed_image_path = trans_dir / img['image']
                        transformed_image_path.parent.mkdir(parents=True, exist_ok=True)
                        if png:
                            save_image_as_png(transformed_image, str(transformed_image_path.with_suffix('.png')))
                        else:
                            save_image_as_exr(transformed_image, str(transformed_image_path.with_suffix('.exr')))

class MyTask:
    def __init__(self, scene, camera, buff_type, shader, ref, images, image_loader_str, results_dir, metric_pattern, config):
        self.scene = scene
        self.camera = camera
        self.config = get_config(config, scene, camera)
        self.buff_type = buff_type
        self.shader = shader
        self.ref_path = ref
        self.image_paths = images
        self.image_loader_str = image_loader_str
        self.results_dir = results_dir
        self.metric_pattern = metric_pattern
        self.results = []

    def run(self):
        set_base_path(str(self.results_dir)) # This is a global
        imageLoader = ImageLoaderFactory.create(self.image_loader_str)
        metrFns = {metric: metric_fn for metric, metric_fn in metric_fns.items() if re.match(self.metric_pattern, metric) }
        ref_data = imageLoader(self.ref_path, self.config)
        for img in self.image_paths:
            noisy_data = imageLoader(img, self.config)
            self.results.append(compute_score(ref_data, noisy_data, self.image_loader_str, metrFns))
        return self

def iterate_tasks(tasks, cores):
    if cores == 1:
        for task in tasks:
            yield task.run()
    else:
        with ProcessPoolExecutor(max_workers=cores) as executor:
            # futures = executor.map(lambda x: x.run(), tasks)
            futures = [executor.submit(task.run) for task in tasks]
            for future in as_completed(futures):
                yield future.result()

def compute_scores(g_image_map, image_counter, ref_index, cores, config):
    tasks = []

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

                ref_image = images[ref_index]
                for shader, img_list in shaders_image_map.items():
                    if shader == ref_name:
                        continue  # Skip the reference shader
                    
                    task = MyTask(scene, camera, buff_type, shader, 
                                    ref_image['image'], [img['image'] for img in img_list],
                                    imageLoaderStr, get_base_path(), metric_pattern, config)
                    tasks.append(task)

    for res in iterate_tasks(tasks, cores):
        img_list = g_image_map[res.scene][res.camera][res.buff_type][res.shader]
        for i, img in enumerate(img_list):
            img['score'] = res.results[i]
        bar.update(len(res.image_paths))
    bar.close()

# compare images with the same sequence number, same buffer type, scene and camera
def aggregate_score(image_1_score, image_2_score):
    scores = []
    for metric, score_1 in image_1_score.items():
        score_2 = image_2_score[metric]
        if score_1 is None or score_2 is None or not re.match(metric_pattern, metric):
            continue
        score = score_1 > score_2 if metric in ['hdrvdp3', 'psnr', 'ssim'] else score_2 > score_1
        scores.append(score)
    
    # cnt = sum(1 for score in scores if score > 1)
    # Avoid division by zero by doing compares above and counting here
    sums = sum(scores)

    return sums

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
                filtered_images = [images for shader, images in shaders_image_map.items() if re.match(shader_pattern, shader)]
                for images in filtered_images:
                    for img in images:
                        if 'score' not in img: continue
                        for metric, score in img['score'].items():
                            if re.match(metric_pattern, metric):
                                metrics.add(metric)
                num_plots += len(metrics)
                # Handle aggregate plot counting
                count_filt_images = [any('score' in img for img in images) for images in filtered_images]
                if len(metrics) > 1 or sum(count_filt_images) > 1:
                    num_plots += 1

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
                scores = defaultdict(lambda: defaultdict(list))
                for shader, images in shaders_image_map.items():
                    if not re.match(shader_pattern, shader):
                        continue
                    for img in images:
                        if 'score' not in img:
                            continue  # Skip images without scores
                        for metric, score in img['score'].items():
                            if score is not None and re.match(metric_pattern, metric):
                                scores[metric][shader].append((img['sequence_number'], score))
                
                # Generate aggregate score
                for shader_1, images_1 in shaders_image_map.items():
                    if not re.match(shader_pattern, shader_1):
                        continue

                    aggr_score_map = defaultdict(int)
                    for shader_2, images_2 in shaders_image_map.items():
                        if shader_1 == shader_2 or not re.match(shader_pattern, shader_2):
                            continue

                        image_2_seqs_iter = iter(images_2)
                        for image_1 in images_1:
                            image_seq = image_1['sequence_number']
                            image_2 = None
                            while (image_2 := next(image_2_seqs_iter, None)) is not None and image_seq != image_2['sequence_number']:
                                pass
                            if image_2 is None:
                                continue

                            if 'score' not in image_1 or 'score' not in image_2:
                                continue  # Skip images without scores

                            aggr_score_map[image_seq] += aggregate_score(image_1['score'], image_2['score'])

                    for seq, aggr_score in aggr_score_map.items():
                        scores['aggregate'][shader_1].append((seq, aggr_score))

                # Plot data for each metric, one plot per metric
                for metric, shaders in scores.items():
                    plt.figure(figsize=(10, 6))
                    plt.title(f'{scene} - {camera} - {buff_type} [{imageLoaderStr}]')
                    plt.xlabel('Samples (4^x)')
                    plt.ylabel(metric.upper())  # Metric name as y-axis label
                    for shader, scores in sorted(shaders.items()):
                        x, y = zip(*scores) # x = range(len(scores))
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
    parser.add_argument('--results-dir', type=str, default='results', help='Path to the Results directory containing images for comparison.')
    parser.add_argument('--output-dir', type=str, default='plots', help='Directory to save the output plot and scores to.')
    parser.add_argument('--image-loader', type=str, default='rgb_aces_tm_nogamma', help='Which loader to use when loading EXR images.')
    parser.add_argument('--scores-file', type=str, default='scores.json', help='Name of the scores JSON file to load/save.')
    parser.add_argument('--config-file', type=str, default='', help='Configuration file containing scene and camera configurations. Currently used for crops only.')
    parser.add_argument('--plot-only', action='store_true', help='If set, only plot the graph without recomputing scores.')
    parser.add_argument('--generate-images', action='store_true', help='If set and config-file is provided, generate cropped images (original EXR) and save them in the results directory.')
    parser.add_argument('--cores', default=1, type=int, help='Number of cores to use. 0 uses maximum.')
    parser.add_argument('--ref-index', default=-1, type=int, help='Which reference sequence number to use from the ref directory. Default is the last sequence number (-1) in the ref directory.')
    parser.add_argument('--blur', type=int, default='0', help='Blur')
    parser.add_argument('--downsample', type=int, default='0', help='Downsample')

    # List-based
    parser.add_argument('--metrics', default='flip,hdrvdp3,mse,psnr,ssim,lpips', help='The metric name to use for comparison. Default all metrics.')
    parser.add_argument('--buffer-types', default='diff_acc,spec_acc,caus_acc,rad_acc', help='The buffer types to use for comparison. Defaults to all buffer types.')
    parser.add_argument('--shaders', default='pt,lt,lt_opt,lt_imp_dist,lt_imp_dist_cam,lt_imp_dist_cam_rt', help='The shaders to use for comparison. Defaults to all shaders.')

    args = parser.parse_args()

    global imageLoaderStr, imageLoader, file_pattern, shader_pattern, metric_pattern, buffer_pattern
    imageLoaderStr = args.image_loader
    imageLoader = ImageLoaderFactory.create(imageLoaderStr)

    metrics = comma_to_list(args.metrics)
    buffer_types = comma_to_list(args.buffer_types)
    shaders = comma_to_list(args.shaders)
    cores = args.cores if args.cores > 0 else None

    if not(metrics and buffer_types and shaders):
        print("Please specify at least one buffer type, shader, and metric.")
        parser.print_help()
        return

    file_pattern = fr"^(?P<name>.*)_(?P<shader>{'|'.join(shaders)}|ref)_(?P<buffer_type>{'|'.join(buffer_types)})_(?P<sequence_number>\d+)(?:\.(?P<extension>\w+))?$"
    shader_pattern = fr"^({'|'.join(shaders)}|ref)$"
    buffer_pattern = fr"^({'|'.join(buffer_types)})$"
    metric_pattern = fr"^({'|'.join(metrics)})$"
    
    results_dir = Path(args.results_dir)
    output_dir  = Path(args.output_dir)
    scores_file  = output_dir / Path(args.scores_file)
    output_dir.mkdir(parents=True, exist_ok=True)

    set_base_path(str(results_dir)) # This is a global

    if args.plot_only:
        g_image_map = load(scores_file)
    else:
        config = load(args.config_file) if args.config_file else {}
        g_image_map, image_counter = scan_directory(results_dir)
        if args.generate_images:
            generate_images(g_image_map, config, output_dir)
            return
        compute_scores(g_image_map, image_counter, args.ref_index, cores, config)
        save(scores_file, g_image_map)

    plot_scores(g_image_map, output_dir)

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()
