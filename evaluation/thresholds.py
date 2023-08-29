import pywt
import numpy as np
from skopt.space import Real

# class Space:
#     def __init__(self, data):
#         self.min = np.min(data)
#         self.max = np.max(data)
#         self.mean = np.mean(data)
#         self.std = np.std(data)
#         self.var = np.var(data)

class Threshold:
    def __init__(self, name) -> None:
        self.name = name
    def get_space(self, space):
        pass
    def fn(self, x, t, m = 0):
        pass

class MultiplicationThreshold(Threshold):
    def __init__(self, name) -> None:
        super().__init__(name)
    def get_space(self, space):
        return list(map(lambda x: Real(0, 1), space))
    def fn(self, x, t, m = 0):
        return x * t

class PywtThreshold(Threshold):
    def __init__(self, name) -> None:
        super().__init__(name)
    def get_space(self, space):
        return list(map(lambda x: Real(0 if self.name != "soft" and self.name != "garrote" else 0.001, x), space))
    def fn(self, x, t, m = 0):
        return pywt.threshold(x, t, self.name, m)

class ThresholdFactory:
    # Method returned expects (input, t, substitute)
    @staticmethod
    def create(threshold_name):
        name = threshold_name.strip().lower()
        if (name == "mult"):
            return MultiplicationThreshold(name)
        if (name == "soft" or name == "hard" or name == "garrote"):
            return PywtThreshold(name)
        else:
            raise ValueError(f"Invalid threshold name {threshold_name}")
    