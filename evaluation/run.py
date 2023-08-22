import sys
import os
import argparse
import jsonpickle
import multiprocessing
import tqdm

sys.path.append(os.getcwd())

from metric import MetricFactory
from thresholds import ThresholdFactory
from search import SearchFactory
from denoiser import *
from denoiser_factory import *
from utils.versioning import get_version

class ParameterSpace:
    def __init__(self):
        self.images = [] # each element is a tuple (ref, images)
        self.metrics = [] # MSE, SSIM
        self.thresholds = [] # mult, soft, hard, garrote
        self.searchMethods = [] # naive, gp_minimize
        self.coefficientLengths = [] # how many coefficients should we optimise for? this is highly dependent on the method
        self.iterations = [] # applies to ALL
        self.denoisers = [] # fourier, wavelet, wavelet_swt, curvelet etc

class RunResult:
    def __init__(self, denoiserParams, denoiserResult):
        self.denoiserParams = denoiserParams
        self.denoiserResult = denoiserResult

class Progress:
    def __init__(self, fn):
        self.callback = fn
    def update(self, current, total):
        self.callback(current, total)

class Run:
    def __init__(self, parameterSpace, cores = 1, monitoringFn=lambda n,d: None):
        self.parameterSpace = parameterSpace
        self.progress = Progress(monitoringFn)
        self.cores = max(1, cores)
        self.runsCompleted = 0
        self.totalRuns = 0
        self.runs = []
        self.version = get_version().to_dict()

    @staticmethod
    def _task(dp):
        pairImage = dp.pairImage
        coeff = dp.coefficientLength
        iteration = dp.iterations
        metricMethod = MetricFactory.create(dp.metric)
        thresholdMethod = ThresholdFactory.create(dp.thresholding)
        searchMethod = SearchFactory.create(dp.search)
        denoiserMethod = DenoiserFactory.create(dp.denoiser)
        denoiserParams = DenoiserRunParams((pairImage[0], pairImage[1]), metricMethod, thresholdMethod, searchMethod, coeff, iteration, denoiserMethod)
        return RunResult(dp, denoiserMethod.run(denoiserParams))

    def _update(self, _):
        self.runsCompleted += 1
        self.progress.update(self.runsCompleted, self.totalRuns)
    
    def run(self):
        for p in self.parameterSpace:
            denParams = []
            for denoiserName in p.denoisers:
                for img in p.images:
                    refImage = img[0]
                    images = img[1]
                    for image in images:
                        for metric in p.metrics:
                            for threshold in p.thresholds:
                                for searchMethodName in p.searchMethods:
                                    for coeff in p.coefficientLengths:
                                        for iteration in p.iterations:
                                            denoiserParamsString = DenoiserRunParamsString((refImage, image), metric, threshold, searchMethodName, coeff, iteration, denoiserName)
                                            denParams.append(denoiserParamsString)

        self.totalRuns = len(denParams)
        # distribute tasks using multiprocessing
        if (self.cores == 1):
            for denoiserParams in denParams:
                self.runs.append(Run._task(denoiserParams))
                self._update(None)
        else:
            pool = multiprocessing.Pool(processes=min(self.cores, len(denParams)))
            asyncResults = list(map(lambda dp: pool.apply_async(Run._task, (dp,), callback=self._update), denParams))
            pool.close()
            pool.join()
            self.runs = list(map(lambda x: x.get(), asyncResults))

def save(file_name, obj):
        with open(file_name, 'w') as fp:
            fp.write(jsonpickle.encode(obj)) # use , make_refs=False to avoid the py/id stuff. or unpicklable=False (extreme)
    
def load(file_name):
    with open(file_name, 'r') as fp:
        return jsonpickle.decode(fp.read())

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Evaluates denoising using the parameter space provided in the input json file.\n{versionString}')
    parser.add_argument('--config', default='config.json', help='File path to the JSON ParameterSpace object')
    parser.add_argument('--result', default='result.json', help='Where to save the JSON Run object')
    parser.add_argument('--cores', default=0, help='Number of cores to use. 0 uses maximum')
    args = parser.parse_args()

    configPath = args.config
    resultPath = args.result
    cores = args.cores if args.cores > 0 and args.cores <= multiprocessing.cpu_count() else multiprocessing.cpu_count()
    print(f'Reading ParameterSpace from \'{configPath}\' and writing result to \'{resultPath}\'. Max cores: {cores}')
    print(versionString)

    parameterSpace = load(configPath)
    bar = tqdm.tqdm()
    def update(n ,d):
        bar.total = d
        bar.update(1)
    run = Run(parameterSpace, cores, update)
    run.run()
    bar.close()

    save(resultPath, run)

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()
