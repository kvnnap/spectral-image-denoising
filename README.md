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
            "rgb",
            "rgb_tm"
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
                ]
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
                "name": "curvelet" // curvelet has no additional config yet
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

## Matlab hdrvdp3 integration

See matlab folder for the scripts that were used to generate the hdrpy package/module

Current metric is hardcoded with settings for 24 inch Full HD display, observed from 30cm distance

### Downgrade

Needed to downgrade to bullseye because matlab install a C++ standard library that is old. 
One workaround is to simply delete this old library from the Matlab sys os folder (and possibly others)

see here for more info:

https://www.mathworks.com/matlabcentral/answers/1907290-how-to-manually-select-the-libstdc-library-to-use-to-resolve-a-version-glibcxx_-not-found



