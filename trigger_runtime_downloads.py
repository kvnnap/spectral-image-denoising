# Trigger LPIPS and/or other runtime downloaded artefacts.

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import evaluation.metric

if __name__ == "__main__":
    print('trigger_runtime_downloads.py executed!')
