# python-image-processing

## Arguments

```bash
usage: run.py [-h] [--config CONFIG] [--result RESULT] [--temp TEMP] [--cores CORES]

Evaluates denoising using the parameter space provided in the input json file.

options:
  -h, --help       show this help message and exit
  --config CONFIG  File path to the JSON ParameterSpace list (default=config.json)
  --result RESULT  Where to save the JSON Run object (default=result.json)
  --image-base PTH Where to load images from (default='')
  --temp TEMP      Where to save intermediate JSON Run objects (default=temp.json)
  --cores CORES    Number of cores to use. 0 uses maximum (default=0)
```
## Configuration

The below JSON configuration outlines all possible values for a group of runs.

For wavelet families and possible variations see https://pywavelets.readthedocs.io/en/latest/regression/wavelet.html

For searchMethods look at https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
The options we're giving below are for bounded variables (which is what we're using)
"L-BFGS-B" is the default method

```json
[
    {
        "py/object": "core.run.ParameterSpace",
        "name": "group_run_name",
        "samples": 1,
        "images": [
            {
                "py/tuple": [
                    "ground_truth.raw",
                    [
                        "noisy.raw"
                    ]
                ]
            }
        ],
        "imageLoaders":[
            "gray",
            "gray_tm",
            "gray_tm_nogamma",
            "gray_aces_tm",
            "gray_aces_tm_nogamma",
            "rgb",
            "rgb_tm",
            "rgb_tm_nogamma",
            "rgb_aces_tm",
            "rgb_aces_tm_nogamma"
        ],
        "metrics": [
            "mse",
            "ssim",
            "mse_ssim",
            "psnr",
            "hdrvdp3",
            "flip"
        ],
        "thresholds": [
            "mult",
            "hard",
            "soft",
            "garrote"
        ],
        "searchMethods": [
            "naive",
            "naive_descending",
            "gp_minimize",
            {
                "name": "minimize",
                "method": [ // L-BFGS-B is default if not method is given
                    "Nelder-Mead", "L-BFGS-B", "TNC", "SLSQP", "Powell", "trust-constr", "COBYLA"
                ],
                "x": [ [1,4,0,1] ] // Put starting coeffs here
            }
        ],
        "iterations": [
            100
        ],
        "denoisers": [
            {
                "name": "fourier",
                "coefficientLength": [ // 16 is default
                    16
                ]
            },
            {
                "name": "wavelet",
                "level": [  // 0 is default
                    0
                ],
                "waveletName": [ // Name + number. sym2 is default.
                    "haar", "db", "sym", "coif", "bior", "rbio", "dmey", "gaus", "mexh", "morl", "cgau", "shan", "fbsp", "cmor"
                ]
            },
            {
                "name": "wavelet_swt",
                "level": [ // 0 is default
                    6
                ],
                "waveletName": [ // Name + number. sym2 is default.
                    "haar", "db", "sym", "coif", "bior", "rbio", "dmey", "gaus", "mexh", "morl", "cgau", "shan", "fbsp", "cmor"
                ]
            },
            {
                "name": "curvelet", // curvelet - if sectors true will compute ALL coefficients. Default is false (Which computes only the circular ones)
                "sectors": [ true ] 
            }
        ]
    },
    // Other possible groups here
]
```

## Important

Copy your licenced copy of *CurveLab-2.1.3.tar.gz* inside the *.devcontainer* folder before building!

## Install python requirements

```bash
./install_pips.sh
```
or

```bash
pip3 install -r requirements.txt
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Information
These scripts can import RAW files which container HDR images. The format is:

```C++
struct Vector3 
{
    float r, g, b;
}
struct RawFormat
{
    int width;
    int height;
    std::vector<Vector3> pixels; // length width*height
}
```
## Other

Update requirements.txt using
```bash
pip3 freeze > requirements.txt
```

Add version information. This will generate version.py

```bash
./postbuild.sh
```

Generate Docker image
```bash
docker build -t kvnnap/python-image-processing .
docker push kvnnap/python-image-processing
docker run --rm -it -v $PWD:/app/data kvnnap/python-image-processing --cores 12
```

## Recovery

```bash
docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/recover.py --cores 12
```

## Visualisation

```bash
docker run --rm -it --entrypoint python3 --env DISPLAY=:0 -v /tmp/.X11-unix:/tmp/.X11-unix -v $PWD:/app/data kvnnap/python-image-processing /app/visualisation/run.py --result paper_exp_1-result.json --image-base images/exp_1
```

maybe can also alias.

```bash
alias result_viewer="docker run --rm -it --entrypoint python3 --env DISPLAY=:0 -v /tmp/.X11-unix:/tmp/.X11-unix -v $PWD:/app/data kvnnap/python-image-processing /app/visualisation/run.py"

result_viewer --result paper_exp_1-result.json --image-base images/exp_1
```

## Merge

```bash
docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/merge.py --result r1.json --result r2.json --result r3.json --merged-result merged.json
```

## MSE FIX
```bash
docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/fix_mse.py --result res.json --fixed-result merged.json --image-base images/exp_1
```

## Cosine similarity
```bash
docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/cosine_similarity_interactive.py --result res.json
```

## PNG image extraction from EXR
```bash
docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/image_convert.py --image smb/seeded-images --image-loader gray_aces_tm --destination smb/seeded-images-png
```
## Runs image extraction to either EXR/PNG
```json
"args": [
    "--result", "smb/exp_1c/runs_merged.json",
    "--image-base", "smb/seeded-images", 
    "--formats", "png", 
    "--pre-image-loader", "",
    "--post-procs", "", 
    "--out-dir", "offline/paper-data/runs-denoised"
]
```
```bash
docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/generate_run_images.py <args-above>
```

## Best scorers extraction for samples generation (for confidence interval) example
```bash
docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/extract_top_config.py --result smb/exp_1b/result_gray_all_merged.json --image-loaders gray_aces_tm --metrics hdrvdp3,mse,psnr,ssim --out-config smb/exp_1c/config_top_runs.json
```

## Matlab hdrvdp3 integration

See matlab folder for the scripts that were used to generate the hdrpy package/module

Current metric is hardcoded with settings for 24 inch Full HD display, observed from 30cm distance

### Downgrade

Needed to downgrade to bullseye because matlab install a C++ standard library that is old. 
One workaround is to simply delete this old library from the Matlab sys os folder (and possibly others)

see here for more info:

https://www.mathworks.com/matlabcentral/answers/1907290-how-to-manually-select-the-libstdc-library-to-use-to-resolve-a-version-glibcxx_-not-found


# Paper Extraction Process

The following is a step-by-step guide of the process and commands executed. Some runs were actually split on multiple servers, to increase concurrency. Here, we assume only one machine is going to compute these runs.

## Runs

The runs were generated using all six configs in paper_data/configs. These can all be merged in one config if needed. The flip variants are separate because they run faster on a machine with a GPU.

- config_gray_all_flip.json
- config_gray_all.json
- config_gray_aces_all_flip.json
- config_gray_aces_all.json
- config_gray_aces_nogamma_all_flip.json
- config_gray_aces_nogamma_all.json

Example of running *config_gray_aces_nogamma_all.json* above:

```bash
docker run --rm -it --gpus all -v $PWD/smb:/app/data kvnnap/python-image-processing --cores 4 --image-base seeded-images --config config_gray_aces_nogamma_all.json --result result_gray_aces_nogamma_all.json --temp temp_gray_aces_nogamma_all.json
```

This will generate a result **WITHOUT** all metrics computed for each run. To include all metrics, run the `add_all_metrics.py` script. This adds the 'bestMetricResults' field in each result.

The ultimate paper results were generated only with *config_gray_aces_nogamma_all* and *config_gray_aces_nogamma_all_flip* json files. The ultimate results from these were saved to *runs_merged.json*.

Results can be visualised as explained above.

## Table Extraction

In this particular experiment we were intersted in the first scoring result for each scene and each metric. Eight scenes were examined and there are five metrics which generate 40 results. To extract the tables, in LaTeX or CSV, the `extract_score.py` script is used. The previous result is input, the image loader param is set to *gray_aces_tm_nogamma* (for this experiment) and out-table param is the path of the output table. The use-best-metrics param is set to sort the results using all metrics combined before extracting the first scoring result.

An example of table extraction:

```bash
extract_score.py --result result_gray_aces_nogamma_all.json --image-loaders gray_aces_tm_nogamma --out-table config_top_runs_gray_aces_tm_ng_bm
```

Used:

```json
["--result", "paper_data/result_gray_all_merged.json", "--out-table", "paper_data/tables"],
["--result", "paper_data/result_gray_all_merged.json", "--out-table", "paper_data/tables_bm", "--use-best-metrics"]
```

### STAR Tables Extraction

To generate the scores for the ReLaX, ReBLUR and Optix denoisers, the `extract_star_score.py` script is used. This script assumes suffix **_8** to be the ref image in the *--ref-image-dir* parameter. All noise levels _0, _1, etc in *--noisy-image-dir* are loaded and scores are stored in the *--result* file path (json). Hint. Ref images are in the seeded-images directory.

## Statistical analysis

In this particular experiment we were intersted in the first scoring result for each scene and each metric. Eight scenes were examined and there are five metrics which generate 40 results. The `extract_top_config.py` script is given a result, like *result_gray_aces_nogamma_all.json* and generates a config and a runData file. The config file is the input for a further run, which computes the first scoring runs for a hundred times. This result is then used to generate statistical confidence. The runData is a file that contains only the first scorers in it. It can be useful for viewing or generating other data faster.

Args used (for normal) - renamed to runs_merged.json:

```json
[
    "--result", "paper_data/result_gray_all_merged.json",
    "--out-config", "paper_data/config_runs.json",
    "--image-loaders", "gray_aces_tm_nogamma"
]
```

Args used (for best metrics) - renamed to runs_best_metric.json:

```json
[
    "--result", "paper_data/result_gray_all_merged.json",
    "--out-config", "paper_data/config_runs_best_metrics.json",
    "--image-loaders", "gray_aces_tm_nogamma",
    "--use-best-metrics"
]
```

## Image Extraction

The `generate_run_images.py` script is used to apply the inverse transform and get back the denoised images. Grayscale coeffs can be applied to RGB channels using *--pre-image-loader*. *--post-procs* is used to apply further post processing if needed. All the runs in *--result* will be used.

Args used:

```json
[   
    "--result", "paper_data/runs_merged.json", 
    "--image-base", "paper_data/seeded-images", 
    "--post-procs", "aces_tm", 
    "--formats", "png",
    "--out-dir", "paper_data/denoised"
]
```

## Merging image buffers

The `add_exr_images.py` script is used to add/combine source images together (additively). This is useful to combine diffuse, specular and caustic buffers for previewing. Example is below. Images should contain the filename to each buffer.

```json
[
    "--image-base", "paper_data/seeded-images",
    "--images", "caustic_glass_caustics_2.exr, caustic_glass_caustics_7.exr",
    "--post-procs", "aces_tm,gamma",
    "--pre-image-loader", "gray_aces_tm_nogamma",
    "--formats", "png",
    "--out-path", "paper_data/test_image"
]
```

