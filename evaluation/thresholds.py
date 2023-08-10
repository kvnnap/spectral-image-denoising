import pywt
from functools import partial

class ThresholdFactory:
    # Method returned expects (input, t)
    @staticmethod
    def create(threshold_name):
        name = threshold_name.strip().lower()
        if (name == "mult"):
            return lambda x, t: x * t
        if (name == "soft" or name == "hard" or name == "garrote"):
            return partial(pywt.threshold, mode=name)
        else:
            raise ValueError(f"Invalid threshold name {threshold_name}")
    