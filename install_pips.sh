#!/bin/bash

pip3 install -r requirements.txt
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install later cos dependencies
pip3 install lpips==0.1.4
