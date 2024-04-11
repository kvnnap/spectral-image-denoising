import numpy as np

aces_input_matrix = np.array([
    [0.59719, 0.35458, 0.04823],
    [0.07600, 0.90834, 0.01566],
    [0.02840, 0.13383, 0.83777]
])

aces_output_matrix = np.array([
    [1.60475, -0.53108, -0.07367],
    [-0.10208, 1.10813, -0.00605],
    [-0.00327, -0.07276, 1.07602]
])

def mul(m, v):
    x = m[0,0] * v[0] + m[0,1] * v[1] + m[0,2] * v[2]
    y = m[1,0] * v[0] + m[1,1] * v[1] + m[1,2] * v[2]
    z = m[2,0] * v[0] + m[2,1] * v[1] + m[2,2] * v[2]
    return np.array([x, y, z])

def rtt_and_odt_fit(v):
    a = v * (v + 0.0245786) - 0.000090537
    b = v * (0.983729 * v + 0.4329510) + 0.238081
    return a / b

def aces_fitted(v):
    v = mul(aces_input_matrix, v)
    v = rtt_and_odt_fit(v)
    return mul(aces_output_matrix, v)

a = 1
print(aces_fitted(np.array([a, a, a])))
