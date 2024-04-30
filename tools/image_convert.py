# Convert exr to png, and more - mainly used to gen images for paper

import sys
import os
import glob
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image import save_image_as_png
from utils.versioning import get_version
from evaluation.image_loader import ImageLoaderFactory

def find_exr_files(directory="."):
    exr_files = glob.glob(os.path.join(directory, "*.exr"))
    return exr_files

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Convert images.\n{versionString}')
    parser.add_argument('--image', default='smb/seeded-images', help='Path to image or dir. If empty, will grab all exr images in current directory.')
    parser.add_argument('--image-loader', default='gray_aces_tm', help='Image loader to use. Defaults to gray_aces_tm')
    parser.add_argument('--destination', default='smb/seeded-images-png', help='The destination directory, defaults to current directory')
    args = parser.parse_args()

    destDir = Path(args.destination)
    if not destDir.is_dir():
        print("Destination is not a directory")

    pImage = Path(args.image)
    if args.image and pImage.is_file() and pImage.suffix.strip().lower() == '.exr':
        images = [ args.image ]
    else:
        images = find_exr_files(args.image)

    if not images:
        print("No input images")
        return
    
    imgLoader = ImageLoaderFactory.create(args.image_loader)
    # load and save images
    for imagePath in images:
        pImg = Path(imagePath)
        newFileName = pImg.with_stem(f'{pImg.stem}_{args.image_loader}').with_suffix('.png').name
        print(f'Processing {newFileName}')
        newImagePath = str(destDir.joinpath(newFileName))
        img = imgLoader(imagePath)
        save_image_as_png(img, str(newImagePath))

    print(f'Converted {len(images)} images')
    
# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()