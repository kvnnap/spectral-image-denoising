import sys
import os
import argparse
import multiprocessing as mp
import time
import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.run import RunData, RunResult
from core.denoiser import DenoiserRunParamsString
from metric import MetricFactory
from thresholds import ThresholdFactory
from search import SearchFactory
from denoiser import DenoiserRunParams
from denoiser_factory import DenoiserFactory
from evaluation.image_loader import ImageLoaderFactory
from utils.versioning import get_version
from utils.serialisation import save, load, print_obj
from utils.image import set_base_path

class Progress:
    def __init__(self, fn):
        self.callback = fn
    def update(self, current, total, result):
        self.callback(current, total, result)

class Run:
    def __init__(self, parameterSpace, cores = 1, monitoringFn=lambda n,d,r: None):
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
        iteration = dp.iterations
        imageLoaderMethod = ImageLoaderFactory.create(dp.imageLoader)
        metricMethod = MetricFactory.create(dp.metric)
        thresholdMethod = ThresholdFactory.create(dp.thresholding)
        searchMethod = SearchFactory.create(dp.search)
        denoiserMethod = DenoiserFactory.create(dp.denoiser)
        denoiserParams = DenoiserRunParams((pairImage[0], pairImage[1]), imageLoaderMethod, metricMethod, thresholdMethod, searchMethod, iteration, denoiserMethod)
        try:
            start = time.perf_counter_ns()
            run = denoiserMethod.run(denoiserParams)
            finish = time.perf_counter_ns()
            return RunResult(dp, run, finish - start)
        except Exception as e:
            print(f"Exception in _task: {e}")
            print_obj(dp)
            sys.stdout.flush()
            raise

    def _update(self, result):
        self.runsCompleted += 1
        self.progress.update(self.runsCompleted, self.totalRuns, result)

    @staticmethod
    def get_denoiser_params(parameter_space):
        denParams = []

        for p in parameter_space:
            # Generate list of all possible denoiser configurations
            denoiserConfigs = []
            for denoiserConfig in p.denoisers:
                denoiserConfigs.extend(DenoiserFactory.unpack_config(denoiserConfig))
            
            for denoiserConfig in denoiserConfigs:
                for imageLoader in p.imageLoaders:
                    for img in p.images:
                        refImage = img[0]
                        images = img[1]
                        for image in images:
                            for metric in p.metrics:
                                for threshold in p.thresholds:
                                    for searchMethodName in p.searchMethods:
                                        for iteration in p.iterations:
                                            denoiserParamsString = DenoiserRunParamsString(len(denParams), p.name, (refImage, image), imageLoader, metric, threshold, searchMethodName, iteration, denoiserConfig)
                                            denParams.append(denoiserParamsString)
        return denParams
    
    def run(self):
        denParams = Run.get_denoiser_params(self.parameterSpace)
        self.totalRuns = len(denParams)
        # distribute tasks using multiprocessing
        if (self.cores == 1):
            for denoiserParams in denParams:
                rResult = Run._task(denoiserParams)
                self.runs.append(rResult)
                self._update(rResult)
        else:
            asyncResults = []
            with mp.Pool(processes=min(self.cores, len(denParams)), maxtasksperchild=1) as pool:
                asyncResults = list(map(lambda dp: pool.apply_async(Run._task, (dp,), callback=self._update), denParams))
                pool.close()
                pool.join()
            for asyncResult in asyncResults:
                if asyncResult.successful():
                    self.runs.append(asyncResult.get())
            #self.runs = list(map(lambda x: x.get(), asyncResults))

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Evaluates denoising using the parameter space provided in the input json file.\n{versionString}')
    parser.add_argument('--config', default='config.json', help='File path to the JSON ParameterSpace list')
    parser.add_argument('--result', default='result.json', help='Where to save the JSON Run object')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    parser.add_argument('--temp', default='temp.json', help='Where to save intermediate JSON Run objects')
    parser.add_argument('--cores', default=0, type=int, help='Number of cores to use. 0 uses maximum')
    args = parser.parse_args()

    configPath = args.config
    resultPath = args.result
    tempPath = args.temp
    cores = args.cores if args.cores > 0 and args.cores <= mp.cpu_count() else mp.cpu_count()
    set_base_path(args.image_base)
    print(f'Reading ParameterSpace from \'{configPath}\' and writing result to \'{resultPath}\'. Max cores: {cores}')
    print(versionString)

    parameterSpace = load(configPath)
    bar = tqdm.tqdm()
    def update(n, d, result):
        save(tempPath, result, write_mode='a')
        bar.total = d
        bar.update(1)
    run = Run(parameterSpace, cores, update)
    run.run()
    bar.close()

    runData = RunData(run.parameterSpace, run.cores, run.totalRuns, run.runs, run.version)

    save(resultPath, runData)
    save(f'{resultPath}.norefs.json', runData, False)

# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    mp.set_start_method('spawn')
    main()
