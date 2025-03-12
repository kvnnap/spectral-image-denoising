#!/usr/bin/env bash

# This script generates plots for the thesis scores.

# Compare with 4M results
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 1 --image-loader rgb                    --output-dir graphs/4M/plots_rgb --metrics flip,hdrvdp3,mse,psnr,ssim
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 1 --image-loader rgb_aces_tm_nogamma    --output-dir graphs/4M/plots_rgb_aces_tm_nogamma
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 1 --image-loader rgb_aces_tm            --output-dir graphs/4M/plots_rgb_aces_tm

# Compare with 4M results
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 1 --image-loader gray                    --output-dir graphs/4M/plots_gray --metrics flip,hdrvdp3,mse,psnr,ssim
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 1 --image-loader gray_aces_tm_nogamma    --output-dir graphs/4M/plots_gray_aces_tm_nogamma
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 1 --image-loader gray_aces_tm            --output-dir graphs/4M/plots_gray_aces_tm

# Compare with 1M results
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 0 --image-loader rgb                   --output-dir graphs/1M/plots_rgb --metrics flip,hdrvdp3,mse,psnr,ssim
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 0 --image-loader rgb_aces_tm_nogamma   --output-dir graphs/1M/plots_rgb_aces_tm_nogamma
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 0 --image-loader rgb_aces_tm           --output-dir graphs/1M/plots_rgb_aces_tm

# Compare with 1M results
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 0 --image-loader gray                   --output-dir graphs/1M/plots_gray --metrics flip,hdrvdp3,mse,psnr,ssim
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 0 --image-loader gray_aces_tm_nogamma   --output-dir graphs/1M/plots_gray_aces_tm_nogamma
python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results --ref-index 0 --image-loader gray_aces_tm           --output-dir graphs/1M/plots_gray_aces_tm

