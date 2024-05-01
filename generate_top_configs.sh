#!/bin/bash

gen_config="docker run --rm -it --entrypoint python3 -v $PWD/smb:/app/data kvnnap/python-image-processing /app/tools/extract_top_config.py"

$gen_config --result exp_1b/result_gray_all_merged.json --image-loaders gray_aces_tm_nogamma --metrics hdrvdp3,mse,psnr,ssim --out-config exp_1c/config_top_runs_gray_aces_tm_ng.json
$gen_config --result exp_1b/result_gray_all_merged.json --image-loaders gray_aces_tm_nogamma --metrics flip --out-config exp_1c/config_top_runs_gray_aces_tm_ng_flip.json
$gen_config --result exp_1b/result_gray_all_merged.json --image-loaders gray_aces_tm_nogamma --use-best-metrics --out-config exp_1c/config_top_runs_gray_aces_tm_ng_best_metrics.json

# gen_config --result exp_1b/result_gray_all_merged.json --image-loaders gray --metrics hdrvdp3,mse,psnr,ssim --out-config exp_1c/config_top_runs_gray.json
# gen_config --result exp_1b/result_gray_all_merged.json --image-loaders gray --metrics flip --out-config exp_1c/config_top_runs_gray_flip.json
# gen_config --result exp_1b/result_gray_all_merged.json --image-loaders gray --use-best-metrics --out-config exp_1c/config_top_runs_gray_best_metrics.json

# Feanor and Sandro - others
docker run --rm -it -v $PWD:/app/data kvnnap/python-image-processing --cores 8 --image-base seeded-images --config exp_1c/config_top_runs_gray_aces_tm_ng.json --result exp_1c/result_top_runs_gray_aces_tm_ng_1.json --temp exp_1c/temp_top_runs_gray_aces_tm_ng_1.json --split 2,1,1

# recover
docker run --rm -it -v $PWD:/app/data kvnnap/python-image-processing --cores 12 --image-base seeded-images --missing-only --result exp_1c/result_top_runs_gray_aces_tm_ng.json --temp exp_1c/temp_top_runs_gray_aces_tm_ng_0.json --missing-result exp_1c/result_top_runs_gray_aces_tm_ng_0.json --split 2,0,1
docker run --rm -it -v $PWD/offline:/app/data kvnnap/python-image-processing --cores 8 --image-base seeded-images --missing-only --result exp_1c/result_top_runs_gray_aces_tm_ng.json --temp exp_1c/temp_top_runs_gray_aces_tm_ng_1.json --missing-result exp_1c/result_top_runs_gray_aces_tm_ng_1.json --split 2,1,1

# Flip
docker run --rm -it -v $PWD:/app/data kvnnap/python-image-processing --cores 4 --image-base seeded-images --config exp_1c/config_top_runs_gray_aces_tm_ng_flip.json --result exp_1c/result_top_runs_gray_aces_tm_ng_flip.json --temp exp_1c/temp_top_runs_gray_aces_tm_ng_flip.json

docker run --rm -it --gpus all -v $PWD/smb:/app/data kvnnap/python-image-processing --cores 4 --image-base seeded-images --config exp_1c/config_top_runs_gray_aces_tm_ng_flip.json --result exp_1c/result_top_runs_gray_aces_tm_ng_flip_0.json --temp exp_1c/temp_top_runs_gray_aces_tm_ng_flip_0.json --split 4,0,3
docker run --rm -it --gpus all -v $PWD/smb:/app/data kvnnap/python-image-processing --cores 4 --image-base seeded-images --config exp_1c/config_top_runs_gray_aces_tm_ng_flip.json --result exp_1c/result_top_runs_gray_aces_tm_ng_flip_1.json --temp exp_1c/temp_top_runs_gray_aces_tm_ng_flip_1.json --split 4,3,1

#Rec uni pc
docker run --rm -it --gpus all -v $PWD/offline:/app/data kvnnap/python-image-processing --cores 6 --image-base seeded-images --missing-only --result exp_1c/result_top_runs_gray_aces_tm_ng_flip.json --temp exp_1c/temp_top_runs_gray_aces_tm_ng_flip_0.json --missing-result exp_1c/result_top_runs_gray_aces_tm_ng_flip_0.json --split 4,0,3

# RUN THIS AT HOME
docker run --rm -it --gpus all -v $PWD/offline:/app/data kvnnap/python-image-processing --cores 4 --image-base seeded-images --missing-only --result exp_1c/result_top_runs_gray_aces_tm_ng_flip.json --temp exp_1c/temp_top_runs_gray_aces_tm_ng_flip_1.json --missing-result exp_1c/result_top_runs_gray_aces_tm_ng_flip_1.json --split 4,3,1


# Mark - Best Results
docker run --rm -it --gpus all -v $PWD/offline:/app/data kvnnap/python-image-processing --cores 8 --image-base seeded-images --config exp_1c/config_top_runs_gray_aces_tm_ng_best_metrics.json --result exp_1c/result_top_runs_gray_aces_tm_ng_best_metrics.json --temp exp_1c/temp_top_runs_gray_aces_tm_ng_best_metrics.json
