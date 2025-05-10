#!/usr/bin/env bash

# This script generates plots for the thesis scores.

# We can generate cropped and save to FileSystem
# And then used these cropped results later.
# We can also use original from /home/vscode/results
# but then the cropping is done in memory. Loading large images
# might be slow so we are testing by generating cropped, saving them
# and then using these cropped results later.

# Generate LT naive ones using - 4M_hdrvdp3 copied  from 4M/plots_rgb_aces_tm_nogamma folder
# python tools/thesis_compare_images_graph.py --plot-only  --output-dir graphs/4M_hdrvdp3/plots_rgb_aces_tm_nogamma --shaders lt --buffer-types caus_acc --metrics hdrvdp3

# Generate cropped again
# python tools/thesis_compare_images_graph.py --results-dir /home/vscode/results/Results_Fixed --config-file crop.json --output-dir results/results_cropped --generate-images
# python tools/thesis_compare_images_graph.py --results-dir /home/vscode/results/Results_Fixed --config-file blur.json --output-dir results/results_blurred --generate-images
# python tools/thesis_compare_images_graph.py --results-dir /home/vscode/results/Results_Fixed --config-file downsample.json --output-dir results/results_downsampled --generate-images

# Compare with 4M results (cropped - fixed)
# python tools/thesis_compare_images_graph.py --plot-only  --output-dir graphs/4M_cropped/plots_rgb --metrics flip,hdrvdp3,mse,psnr,ssim
# python tools/thesis_compare_images_graph.py --plot-only  --output-dir graphs/4M_cropped/plots_rgb_aces_tm_nogamma
# python tools/thesis_compare_images_graph.py --plot-only  --output-dir graphs/4M_cropped/plots_rgb_aces_tm

# # Compare with 4M results (crop)
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --config-file crop.json --ref-index 1 --image-loader rgb                  --output-dir graphs/4M_cropped/plots_rgb --metrics flip,hdrvdp3,mse,psnr,ssim
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --config-file crop.json --ref-index 1 --image-loader rgb_aces_tm_nogamma  --output-dir graphs/4M_cropped/plots_rgb_aces_tm_nogamma
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --config-file crop.json --ref-index 1 --image-loader rgb_aces_tm          --output-dir graphs/4M_cropped/plots_rgb_aces_tm

# # Compare with 4M results (downsample)
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --config-file downsample.json --ref-index 1 --image-loader rgb                  --output-dir graphs/4M_downsample/plots_rgb --metrics flip,hdrvdp3,mse,psnr,ssim
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --config-file downsample.json --ref-index 1 --image-loader rgb_aces_tm_nogamma  --output-dir graphs/4M_downsample/plots_rgb_aces_tm_nogamma
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --config-file downsample.json --ref-index 1 --image-loader rgb_aces_tm          --output-dir graphs/4M_downsample/plots_rgb_aces_tm

# # Compare with 4M results (blur)
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --config-file blur.json --ref-index 1 --image-loader rgb                  --output-dir graphs/4M_blur/plots_rgb --metrics flip,hdrvdp3,mse,psnr,ssim
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --config-file blur.json --ref-index 1 --image-loader rgb_aces_tm_nogamma  --output-dir graphs/4M_blur/plots_rgb_aces_tm_nogamma
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --config-file blur.json --ref-index 1 --image-loader rgb_aces_tm          --output-dir graphs/4M_blur/plots_rgb_aces_tm

# Generate cropped
# python tools/thesis_compare_images_graph.py --results-dir /home/vscode/results --config-file thesis_compare.json --generate-images

# Compare with 4M results (cropped)
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir plots/extra --ref-index 1 --image-loader rgb                  --plot-only  --output-dir graphs/4M_cropped/plots_rgb --metrics flip,hdrvdp3,mse,psnr,ssim
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir plots/extra --ref-index 1 --image-loader rgb_aces_tm_nogamma  --plot-only  --output-dir graphs/4M_cropped/plots_rgb_aces_tm_nogamma
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir plots/extra --ref-index 1 --image-loader rgb_aces_tm          --plot-only  --output-dir graphs/4M_cropped/plots_rgb_aces_tm

# # Compare with 4M results
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 1 --image-loader rgb                    --output-dir graphs/4M/plots_rgb --metrics flip,hdrvdp3,mse,psnr,ssim
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 1 --image-loader rgb_aces_tm_nogamma    --output-dir graphs/4M/plots_rgb_aces_tm_nogamma
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 1 --image-loader rgb_aces_tm            --output-dir graphs/4M/plots_rgb_aces_tm

# # Compare with 4M results
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 1 --image-loader gray                    --output-dir graphs/4M/plots_gray --metrics flip,hdrvdp3,mse,psnr,ssim
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 1 --image-loader gray_aces_tm_nogamma    --output-dir graphs/4M/plots_gray_aces_tm_nogamma
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 1 --image-loader gray_aces_tm            --output-dir graphs/4M/plots_gray_aces_tm

# # Compare with 1M results
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 0 --image-loader rgb                   --output-dir graphs/1M/plots_rgb --metrics flip,hdrvdp3,mse,psnr,ssim
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 0 --image-loader rgb_aces_tm_nogamma   --output-dir graphs/1M/plots_rgb_aces_tm_nogamma
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 0 --image-loader rgb_aces_tm           --output-dir graphs/1M/plots_rgb_aces_tm

# # Compare with 1M results
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 0 --image-loader gray                   --output-dir graphs/1M/plots_gray --metrics flip,hdrvdp3,mse,psnr,ssim
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 0 --image-loader gray_aces_tm_nogamma   --output-dir graphs/1M/plots_gray_aces_tm_nogamma
# python tools/thesis_compare_images_graph.py --cores 4 --results-dir /home/vscode/results/Results_Fixed --ref-index 0 --image-loader gray_aces_tm           --output-dir graphs/1M/plots_gray_aces_tm

