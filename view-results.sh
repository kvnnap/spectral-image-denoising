#!/bin/bash

docker run --rm -it --entrypoint python3 --env DISPLAY=:0 -v /tmp/.X11-unix:/tmp/.X11-unix -v $PWD:/app/data kvnnap/python-image-processing /app/visualisation/run.py \
	--result results/paper_exp_1-result.json \
	--result results/paper_exp_1_gmsessim-result.json \
    --result results/paper_exp_1_gray-result.json \
	--image-base images/exp_1

