import numpy as np
import matplotlib.pyplot as plt

import scipy.optimize as spo


def f(x):
    return x[0]**2 - 12*x[0] + 20 + x[1]**2

x_start = [0, 0]
bounds = [(0, 1), (1, 2)]
result = spo.minimize(f, x_start, bounds=bounds, options={'disp': True})

print(result)
