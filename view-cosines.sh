#!/bin/bash

docker run --rm -it --entrypoint python3 -v $PWD:/app/data kvnnap/python-image-processing /app/tools/cosine_similarity_interactive.py --result results/paper_exp_1_gray_final-result.json


