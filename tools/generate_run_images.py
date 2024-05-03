import sys
import os
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image import alpha_correction_chain, save_image_as_png, save_image_as_exr, set_base_path, tone_map, tone_map_aces
from utils.versioning import get_version
from utils.serialisation import load
from utils.string import comma_to_list, get_prefix
from visualisation.result_image_processor import ResultImageProcessor
from utils.constants import NAMEMAP

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Generate image from coeffs in results.\n{versionString}')
    # smb/exp_1c/runs_merged.json
    parser.add_argument('--result', default='', help='The result to load')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
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

    descString = f'Loading {args.result} '
    descString += f'applying {args.pre_image_loader if args.pre_image_loader else "default"} pre-image loader '
    descString += f'applying {",".join(postProc) if postProc else "no"} post-processing step(s) '
    descString += f'and saving images to {args.out_dir}'
    print(descString)

    runData = load(args.result)

    for i, run in enumerate(runData.runs):
        print(f'\rProgress {i + 1}/{len(runData.runs)}', end='', flush=True)
        rip = ResultImageProcessor(run)

        # Gen filename
        dp = run.denoiserParams
        sceneName = get_prefix(dp.pairImage[0], -2)
        if sceneName in NAMEMAP:
            sceneName = NAMEMAP[sceneName]
        fileName = f'{sceneName}_{dp.metric}_{dp.id}'
        destFilePath = str(Path(args.out_dir).joinpath(fileName))

        # alter image loader to apply coeffs on
        if args.pre_image_loader:
            rip.update_image_loader(args.pre_image_loader)
        (_, den, _) = rip.get(False)

        # Post proc
        for pp in postProc:
            den = ppMap[pp](den)

        # save
        for format in formats:
            formatMap[format](den, destFilePath)

    print('\nCompleted')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()