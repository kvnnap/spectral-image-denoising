#from functools import partial
import numpy as np
import math
from skopt import gp_minimize
import copy

# fn to minimize, space is an array [x[0] range, x[1] range, etc..]
class Result:
    def __init__(self, x_min, x_iters, score_min, scores, scores_global):
        self.x = x_min
        self.x_iters = x_iters
        self.fun = score_min
        self.scores = scores
        self.func_vals = scores_global

# Since n_calls determines the number of times we call fn,
# determine the subdivisions using n_calls for the time being
# Otherwise, we need to attach context to the denoiser
def naive(fn, space, n_calls):
    subdiv = max(math.ceil((n_calls - 1) / len(space)) + 1, 2)
    x = np.zeros_like(space)
    x_subdiv = list(map(lambda x: np.linspace(x.low, x.high, subdiv), space))
    scores = [[]] * len(x_subdiv)
    scores_global = []
    min_score = (float('inf'), [])
    x_iters = []
    c = 0
    for i in range(len(x_subdiv)):
        if (c == n_calls): break # can do it better
        for j in range(0 if i == 0 else 1, len(x_subdiv[i])):
            if (c == n_calls): break # can do it better
            x[i] = x_subdiv[i][j]
            x_copy = copy.deepcopy(x)
            score = fn(x_copy)
            c += 1
            # initialise to first score
            scores[i].append((score, x_copy))
            scores_global.append(score)
            x_iters.append(x_copy)
            if (score < min_score[0]):
                min_score = (score, x_copy)
            else: # could implement differently, but this saves time
                break
    return Result(min_score[1], x_iters, min_score[0], scores, scores_global)

def gp_minimize_wrapper(fn, space, n_calls):
    r = gp_minimize(fn, space, n_calls=n_calls)
    return Result(r.x, r.x_iters, r.fun, None, r.func_vals)

# Method returned expects (fn, space, n_calls)
class SearchFactory:
    @staticmethod
    def create(search_name):
        name = search_name.strip().lower()
        if (name == "naive"):
            return naive
        elif (name == "gp_minimize"):
            return gp_minimize_wrapper
        else:
            raise ValueError(f"Invalid search name {search_name}")
