#!/bin/bash

result="${1:-"results/paper_exp_1_gray-result_clip.json"}"

echo "Viewing cosines for result '$result'"

docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/cosine_similarity_interactive.py \
    --result $result
