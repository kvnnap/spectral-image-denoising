import sys
import os
sys.path.append(os.getcwd())

from metric import MetricFactory
from thresholds import ThresholdFactory
from search import SearchFactory
from denoiser import *

import jsonpickle

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

class Run:
    def __init__(self, parameterSpace):
        self.parameterSpace = parameterSpace
        self.runs = []
    
    def run(self):
        p = self.parameterSpace
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
    


def save(file_name, obj):
        with open(file_name, 'w') as fp:
            fp.write(jsonpickle.encode(obj))
    
def load(file_name):
    with open(file_name, 'r') as fp:
        return jsonpickle.decode(fp.read())

def main():
    ps = ParameterSpace()
    ps.images = [('images/dice_caustics/output_0.raw', ['images/dice_caustics/output_1.raw'])]
    ps.metrics = ['mse']
    ps.thresholds = ['mult']
    ps.searchMethods = ['naive', 'gp_minimize']
    ps.coefficientLengths = [16]
    ps.iterations = [10]
    ps.denoisers = ['fourier']

    run = Run(ps)
    run.run()

    save('run.json', run)

    run2 = load('run.json')

    print(f"Result count: {len(run.runs)}")

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()
