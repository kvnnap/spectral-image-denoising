import sys
import os
import argparse
import jsonpickle

sys.path.append(os.getcwd())

from metric import MetricFactory
from thresholds import ThresholdFactory
from search import SearchFactory
from denoiser import *

class ParameterSpace:
    def __init__(self):
        self.images = [] # each element is a tuple (ref, images)
        self.metrics = [] # MSE, SSIM
        self.thresholds = [] # mult, soft, hard, garrote
        self.searchMethods = [] # naive, gp_minimize
        self.coefficientLengths = [] # how many coefficients should we optimise for? this is highly dependent on the method
        self.iterations = [] # applies to ALL
        self.denoisers = [] # fourier, etc

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
    def __init__(self, parameterSpace, monitoringFn=lambda n,d: None):
        self.parameterSpace = parameterSpace
        self.progress = Progress(monitoringFn)
        self.runs = []

    # def monitorProgress(self, fn):
    #     self.progress = Progress(fn)
    
    def run(self):
        p = self.parameterSpace
        totalRuns = len(p.images) * len(p.metrics) * len(p.thresholds) * len(p.searchMethods) * len(p.coefficientLengths) * len(p.iterations) * len(p.denoisers)
        for denoiserName in p.denoisers:
            denoiserMethod = DenoiserFactory.create(denoiserName)
            for img in p.images:
                refImage = img[0]
                images = img[1]
                for image in images:
                    for metric in p.metrics:
                        metricMethod = MetricFactory.create(metric)
                        for threshold in p.thresholds:
                            thresholdMethod = ThresholdFactory.create(threshold)
                            for searchMethod in p.searchMethods:
                                searchMethod = SearchFactory.create(searchMethod)
                                for coeff in p.coefficientLengths:
                                    for iteration in p.iterations:
                                        denoiserParams = DenoiserRunParams((refImage, image), metricMethod, thresholdMethod, searchMethod, coeff, iteration)
                                        denoiserResult = denoiserMethod.run(denoiserParams)
                                        self.runs.append(RunResult(denoiserParams, denoiserResult))
                                        self.progress.update(len(self.runs), totalRuns)

def save(file_name, obj):
        with open(file_name, 'w') as fp:
            fp.write(jsonpickle.encode(obj))
    
def load(file_name):
    with open(file_name, 'r') as fp:
        return jsonpickle.decode(fp.read())

def main():
    parser = argparse.ArgumentParser(description="Evaluates denoising using the parameter space provided in the input json file")
    parser.add_argument('--config', default='config.json', help='File path to the JSON ParameterSpace object')
    parser.add_argument('--result', default='result.json', help='Where to save the JSON Run object')
    args = parser.parse_args()

    configPath = args.config
    resultPath = args.result
    print(f'Reading ParameterSpace from \'{configPath}\' and writing result to \'{resultPath}\'')

    parameterSpace = load(configPath)
    run = Run(parameterSpace, lambda n, d: print(f'Progress: {n} out of {d}', end='\r'))
    run.run()

    save(resultPath, run)

    print(f'\nResult count: {len(run.runs)}')

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

# def to_dict(obj):
#     if isinstance(obj, list):
#         out = list(map(lambda x: to_dict(x), obj))
#     elif isinstance(obj, tuple):
#         out = tuple(map(lambda x: to_dict(x), obj))
#     elif (hasattr(obj, '__dict__')):
#         out = {}
#         for attr_name, attr_value in obj.__dict__.items():
#             out[attr_name] = to_dict(attr_value)
#     else:
#         out = obj
#     return out