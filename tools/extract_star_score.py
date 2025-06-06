import sys
import os
import re
import argparse
from pathlib import Path
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import *
from utils.constants import METRICS, CONV
from utils.versioning import get_version
from utils.serialisation import load, save, save_text
from utils.string import get_mapped_scene_name, get_prefix, get_suffix, tables_to_csv, tables_to_latex

def find_exr_files(directory):
    glob = '*.exr'
    directory_path = Path(directory)
    exr_files = list(directory_path.glob(glob))
    def sort_key(path):
        match = re.match(r'^(.+?)_(\d+)$', path.stem)
        return (match.group(1), int(match.group(2)))
    return sorted(exr_files, key=sort_key)

# Finds the highest seq number per scene to get the reference
def find_exr_ref_files(directory, ref_num):
    ref_exrs = find_exr_files(directory)
    m = defaultdict(list)
    for ref in ref_exrs:
        match = re.match(r'^(.+?)_(\d+)$', ref.stem)
        m[match.group(1)].append(ref)
    files = []
    for k, refs in m.items():
        files.append(refs[ref_num])
    return files

class DPString:
    def __init__(self, imageLoader):
        self.imageLoader = imageLoader

def compute_score(ref, noisy, imgLoaderStr):
        dp = DPString(imgLoaderStr)
        ret_obj = {
            'flip': local_flip(ref, noisy, dp),
            'hdrvdp3': local_hdrvdp3(ref, noisy, dp),
            'mse': local_mse(ref, noisy, dp),
            'psnr': local_psnr(ref, noisy, dp),
            'ssim': local_ssim(ref, noisy, dp)
        }
        return ret_obj

def generate_scores(args):
    noisyExrs = find_exr_files(args.noisy_image_dir)
    refExrs = find_exr_ref_files(args.ref_image_dir, args.ref_seq_num)

    # Generate pairs
    pairs = []
    for noisy in noisyExrs:
        # Find appropriate seed image
        prefix = get_prefix(noisy.stem)
        ref = next((ref for ref in refExrs if ref.stem.startswith(prefix)), None)
        if ref is None:
            print('Failed to find ref image')
            return
        pairs.append((ref, noisy))


    imgLoader = ImageLoaderFactory.create(args.image_loader)

    scores = []
    for (ref, noisy) in pairs:
        print(f'Processing {noisy.name}')
        noisyImg = imgLoader(str(noisy))
        refImg = imgLoader(str(ref))
        scores.append({
            'ref': ref.name,
            'noisy': noisy.name,
            'score': compute_score(refImg, noisyImg, args.image_loader),
        })

    return scores

def generate_tables(scores):
    # Generate csv
    metrics = METRICS
    conv = CONV
    tables = []
    for nLevel in range(9):
        # Get noisy with spp nLevel
        sppLevel = [x for x in scores if get_suffix(x['noisy']).startswith(str(nLevel))]

        # Generate table
        table = []
        header = ['scene', *metrics]
        table.append(header)

        # Rows
        for noisyScene in sppLevel:
            # data = [str(round(d), 2) for d in noisyScene['score'].values()]
            data = [conv[m](noisyScene['score'][m]) for m in metrics]
            name = get_mapped_scene_name(noisyScene['noisy'])
            row = [name, *data]
            table.append(row)

        tables.append(table)

    return tables

def main():
    # Load images - given star images and seeded-images
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Compare STAR Denoised images.\n{versionString}')
    parser.add_argument('--noisy-image-dir', default='offline/smb/seeded-images', help='Path to noisy images')
    parser.add_argument('--image-loader', default='gray_aces_tm_nogamma', help='Image loader to use. Defaults to gray_aces_tm_nogamma')
    parser.add_argument('--ref-image-dir', default='offline/smb/seeded-images', help='Path to reference images.')
    parser.add_argument('--ref-seq-num', default=-1, type=int, help='Which seq num to use as ref from ref-image-dir. -1 defaults to highest.')
    parser.add_argument('--result', default='offline/smb/seeded-images/result.json', help='Path to where to store result.')
    parser.add_argument('--preload', default='', help='Skips score generation. Regenerates csv table from json')
    args = parser.parse_args()

    if not args.preload:
        params = {
            'noisy-image-dir': args.noisy_image_dir,
            'image-loader': args.image_loader,
            'ref-image-dir': args.ref_image_dir,
            'result': args.result
        }
        scores = generate_scores(args)
        obj = { 'params': params, 'scores': scores }
        save(args.result, obj, False)
        path = args.result
    else:
        obj = load(args.preload)
        params = obj['params']
        scores = obj['scores']
        path = args.preload
    
    paramsStr = '\n'.join([f'{k} = {v}' for k, v in params.items()]) + '\n\n'
    tables = generate_tables(scores)

    # CSV
    csvStr = paramsStr + tables_to_csv(tables)
    csvPath = str(Path(path).with_suffix('.csv'))
    save_text(csvPath, csvStr)

    # LaTeX
    latexStr = paramsStr + tables_to_latex(tables)
    latexPath = str(Path(path).with_suffix('.tex'))
    save_text(latexPath, latexStr)
    
    

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

