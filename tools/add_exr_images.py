# Script used to add exr images together.
# Intended for merging diffuse, specular and caustics buffer
# back together

import sys
import os
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.image_loader import ImageLoaderFactory
from utils.image import alpha_correction_chain, save_image_as_png, save_image_as_exr, set_base_path, tone_map, tone_map_aces
from utils.versioning import get_version
from utils.string import comma_to_list

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Script used to add exr images together.\n{versionString}')
    parser.add_argument('--images', default='', help='Comma separated list of paths of images. --image-base is prepended')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    parser.add_argument('--pre-image-loader', default='rgb', help='How do we load the listed images? rgb, gray, gray_tm, etc')
    parser.add_argument('--post-procs', default='', help='Comma separated aces_tm,tm,gamma')
    parser.add_argument('--formats', default='exr', help='Comma separated exr,png')
    parser.add_argument('--out-path', default='', help='Where to save added image')
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
    imagePaths = comma_to_list(args.images)
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

    descString = f'Loading {", ".join(imagePaths)} '
    descString += f'applying {args.pre_image_loader if args.pre_image_loader else "default"} pre-image loader '
    descString += f'applying {",".join(postProc) if postProc else "no"} post-processing step(s) '
    descString += f'and saving images to {args.out_path}'
    print(descString)

    loader = ImageLoaderFactory.create(args.pre_image_loader)
    image = None

    for i, imagePath in enumerate(imagePaths):
        print(f'\rProgress {i + 1}/{len(imagePaths)}', end='', flush=True)

        # Add images
        img = loader(imagePath)
        if image is None:
            image = img
        else:
            image += img
        
    # Post proc
    for pp in postProc:
        image = ppMap[pp](image)

    # save
    for format in formats:
        formatMap[format](image, args.out_path)

    # Save infoTable
    print('\nCompleted')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()