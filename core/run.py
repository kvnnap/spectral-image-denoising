class ParameterSpace:
    def __init__(self):
        self.name = 'unnamed'
        self.images = [] # each element is a tuple (ref, images)
        self.imageLoaders = [] # gray, gray_tm, rgb, rgb_tm
        self.metrics = [] # MSE, SSIM
        self.thresholds = [] # mult, soft, hard, garrote
        self.searchMethods = [] # naive, naive_descending, gp_minimize
        self.iterations = [] # applies to ALL
        self.denoisers = [] # fourier, wavelet, wavelet_swt, curvelet etc
        self.samples = 1 # How many times are we re-running runs?

class RunResult:
    def __init__(self, denoiserParams, denoiserResult, time):
        self.denoiserParams = denoiserParams
        self.denoiserResult = denoiserResult
        self.time = time

class RunData:
    def __init__(self, parameterSpace, cores, totalRuns, runs, version = 'N/A'):
        self.parameterSpace = parameterSpace
        self.cores = cores
        self.totalRuns = totalRuns
        self.runs = runs
        self.version = version
