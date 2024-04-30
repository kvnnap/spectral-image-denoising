#!/bin/bash

alias gen_config="docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/extract_top_config.py"

gen_config --result smb/exp_1b/result_gray_all_merged.json --image-loaders gray_aces_tm --metrics hdrvdp3,mse,psnr,ssim --out-config smb/exp_1c/config_top_runs_gray_aces_tm.json
gen_config --result smb/exp_1b/result_gray_all_merged.json --image-loaders gray_aces_tm --metrics flip --out-config smb/exp_1c/config_top_runs_gray_aces_tm_flip.json
gen_config --result smb/exp_1b/result_gray_all_merged.json --image-loaders gray_aces_tm --use-best-metrics --out-config smb/exp_1c/config_top_runs_gray_aces_tm_best_metrics.json

# gen_config --result smb/exp_1b/result_gray_all_merged.json --image-loaders gray --metrics hdrvdp3,mse,psnr,ssim --out-config smb/exp_1c/config_top_runs_gray.json
# gen_config --result smb/exp_1b/result_gray_all_merged.json --image-loaders gray --metrics flip --out-config smb/exp_1c/config_top_runs_gray_flip.json
# gen_config --result smb/exp_1b/result_gray_all_merged.json --image-loaders gray --use-best-metrics --out-config smb/exp_1c/config_top_runs_gray_best_metrics.json
