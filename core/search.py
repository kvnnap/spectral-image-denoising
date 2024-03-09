
# fn to minimize, space is an array [x[0] range, x[1] range, etc..]
class Result:
    def __init__(self, x_min, x_iters, score_min, scores_global, message = ''):
        self.x = x_min
        self.x_iters = x_iters
        self.fun = score_min
        self.func_vals = scores_global
        self.message = message
