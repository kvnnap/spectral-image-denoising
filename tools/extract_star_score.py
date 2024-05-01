import sys
import os
import argparse
from pathlib import Path


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.image_loader import ImageLoaderFactory
from evaluation.metric import *
from utils.versioning import get_version
from utils.serialisation import load, save, save_text
from visualisation.result_image_processor import ResultImageProcessor

def find_exr_files(directory, glob = '*.exr'):
    directory_path = Path(directory)
    exr_files = list(directory_path.glob(glob))
    return sorted(exr_files, key=lambda r: r.name)

def get_prefix(text, steps = -1):
    return '_'.join(text.split('_')[:steps])

def get_suffix(text, steps = -1):
    return text.split('_')[steps]

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
    refExrs = find_exr_files(args.ref_image_dir, '*_8.exr')

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
    metrics = ['flip', 'hdrvdp3', 'mse', 'psnr', 'ssim']
    nameMap = {
        'caustic_glass': 'cup',
        'povray_cup': 'cups',
        'povray_dice': 'dice',
        'povray_reflect': 'reflect',
        'povray_test': 'outer',
        'torus': 'torus',
        'veach_bidir': 'egg',
        'water_caustic': 'water',
    }
    conv = {
        'flip':     lambda x: f'{ x:.2e}',
        'hdrvdp3':  lambda x: f'{-x:.2f}',
        'mse':      lambda x: f'{ x:.2e}',
        'psnr':     lambda x: f'{-x:.2f}',
        'ssim':     lambda x: f'{-x:.2f}',
    }
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
            name = get_prefix(noisyScene['noisy'], -2)
            if name in nameMap:
                name = nameMap[name]
            row = [name, *data]
            table.append(row)

        tables.append(table)

    return tables

def tables_to_csv(tables):
    # tables to csv/latex etc
    csvStr = ''
    for i, table in enumerate(tables):
        csvStr += f'Samples 4^{i}\n'
        for row in table:
            csvStr += ','.join(row) + '\n'
        csvStr += '\n\n'
    return csvStr

def array_to_latex_table(array):
    lStr = "\\begin{table}\n"
    lStr += "\\centering\n"
    lStr += "\\begin{tabular}{|" + "c|" * len(array[0]) + "}\n"
    lStr += "\\hline\n"
    
    head, *tail = array
    lStr += " & ".join(map(lambda x: f'\\textbf{{{x}}}', head)) + " \\\\\n"
    lStr += "\\hline\n"
    for row in tail:
        lStr += " & ".join(map(str, row)) + " \\\\\n"
    
    lStr += "\\hline\n"
    lStr += "\\end{tabular}\n"
    lStr += "\\caption{Your caption here.}\n"
    lStr += "\\label{tab:my_table}\n"
    lStr += "\\end{table}\n"
    
    return lStr

def tables_to_latex(tables):
    # tables to csv/latex etc
    lStr = ''
    for i, table in enumerate(tables):
        lStr += f'Samples 4^{i}\n'
        lStr += array_to_latex_table(table)
        lStr += '\n\n'
    return lStr

def main():
    # Load images - given star images and seeded-images
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Compare STAR Denoised images.\n{versionString}')
    parser.add_argument('--noisy-image-dir', default='offline/paper-data/star-denoised/optix-seeded', help='Path to noisy images')
    parser.add_argument('--image-loader', default='gray_aces_tm_nogamma', help='Image loader to use. Defaults to gray_aces_tm_nogamma')
    parser.add_argument('--ref-image-dir', default='offline/smb/seeded-images', help='Path to reference images.')
    parser.add_argument('--result', default='offline/paper-data/star-denoised/optix-seeded/result.json', help='Path to where to store result.')
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

