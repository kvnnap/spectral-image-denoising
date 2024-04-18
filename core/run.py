class ParameterSpace:
    def __init__(self):
        self.name = 'unnamed'
        self.images = [] # each element is a tuple (ref, images)
        self.imageLoaders = [] # gray, gray_tm, gray_tm_nogamma, gray_aces_tm, gray_aces_tm_nogamma, rgb, rgb_tm, rgb_tm_nogamma, rgb_aces_tm, rgb_aces_tm_nogamma
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
        self.bestMetricResults = None
        self.time = time

class RunData:
    def __init__(self, parameterSpace, cores, totalRuns, runs, version = 'N/A'):
        self.parameterSpace = parameterSpace
        self.cores = cores
        self.totalRuns = totalRuns
        self.runs = runs
        self.version = version
