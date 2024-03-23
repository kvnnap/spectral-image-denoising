
# fn to minimize, space is an array [x[0] range, x[1] range, etc..]
class Result:
    def __init__(self, x_min, x_iters, score_min, scores_global, message = ''):
        self.x = x_min
        self.x_iters = x_iters
        self.fun = score_min
        self.func_vals = scores_global
        self.message = message

    def fix(self):
        # Add if missing
        if self.x not in self.x_iters:
            self.x_iters.append(self.x)
            self.func_vals.append(self.fun)

        # Make sure minimum result is x and fun
        m = min(self.func_vals) 
        if m < self.fun:
            mIndex = self.func_vals.index(m) # Note, first occurence
            self.x = self.x_iters[mIndex]
            self.fun = self.func_vals[mIndex]

            
