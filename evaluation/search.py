from functools import partial
import numpy as np
import math
from skopt import gp_minimize
import copy
import scipy.optimize as spo

from core.search import Result

# Since n_calls determines the number of times we call fn,
# determine the subdivisions using n_calls for the time being
# Otherwise, we need to attach context to the denoiser
def naive(descending, fn, space, n_calls):
    subdiv = max(math.ceil((n_calls - 1) / len(space)) + 1, 2)
    x = [s.high if descending else s.low for s in space]
    x_subdiv = list(map(lambda x: np.linspace(x.high, x.low, subdiv).tolist() if descending else np.linspace(x.low, x.high, subdiv).tolist(), space))
    #scores = [[] for _ in range(len(x_subdiv))]
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
            #scores[i].append((score, x_copy))
            scores_global.append(score)
            x_iters.append(x_copy)
            # initialise to first score
            if (score < min_score[0]):
                min_score = (score, x_copy)
            else: # could implement differently, but this saves time
                break
    return Result(min_score[1], x_iters, min_score[0], scores_global)

def gp_minimize_wrapper(fn, space, n_calls):
    r = gp_minimize(fn, space, n_calls=n_calls)
    return Result(r.x, r.x_iters, r.fun.item(), r.func_vals.tolist())

def gen_num_in_bound(start, bound):
    if start == 'mean':
        return np.mean(bound)
    elif start == 'normal':
        return np.clip(np.random.normal(np.mean(bound), np.abs(bound[1] - bound[0]) / (2.0 * 5.0)), *bound)
    else:
        return np.random.uniform(*bound)

def minimize_wrapper(method_name, start, xStart, fn, space, n_calls):
    bounds = [(s.low, s.high) for s in space]
    if xStart is None:
        x0 = [gen_num_in_bound(start, b) for b in bounds]
    else:
        if len(xStart) != len(bounds):
            raise ValueError(f"Invalid initial starting coefficients 'x' length. Expected {len(bounds)}, actual {len(xStart)}")
        for i in range(len(xStart)):
            if xStart[i] < bounds[i][0] or xStart[i] > bounds[i][1]:
                raise ValueError(f"Provided 'x[{i}]={xStart[i]}' is out of bounds {bounds[i]}")
        x0 = xStart

    results = []
    def callback(intermediate_result):
        if isinstance(intermediate_result, spo.OptimizeResult):
            results.append((intermediate_result.x.tolist(), np.float64(intermediate_result.fun).item()))
        else:
            results.append((intermediate_result.tolist(), fn(intermediate_result.tolist())))
    # Info on default method selection
    # if method is None:
    #     # Select automatically
    #     if constraints:
    #         method = 'SLSQP'
    #     elif bounds is not None:
    #         method = 'L-BFGS-B'
    #     else:
    #         method = 'BFGS'
    kwargs = {
        'bounds': bounds,
        'callback': callback
    }
    if n_calls > 0:
        kwargs['options'] = { 'maxfun': n_calls } if method_name == 'tnc' else { 'maxiter': n_calls }
    if method_name is not None:
        kwargs['method'] = method_name
    r = spo.minimize(fn, x0, **kwargs)
    res = Result(r.x.tolist(), [x for (x, _) in results], np.float64(r.fun).item(), [y for (_, y) in results], r.message)
    # Sometimes r is not in the list, or the minimum is not r
    res.fix()
    return res


# Method returned expects (fn, space, n_calls)
class SearchFactory:
    @staticmethod
    def create(search_config):
        name = search_config['name'].strip().lower()
        if (name == "naive"):
            return partial(naive, False)
        elif (name == "naive_descending"):
            return partial(naive, True)
        elif (name == "gp_minimize"):
            return gp_minimize_wrapper
        elif (name == "minimize"):
            method_name = search_config['method'].strip().lower() if 'method' in search_config else None
            start = search_config['start'].strip().lower() if 'start' in search_config else 'mean'
            x = search_config['x'] if 'x' in search_config else None
            return partial(minimize_wrapper, method_name, start, x)
        else:
            raise ValueError(f"Invalid search name {search_config['name']}")
