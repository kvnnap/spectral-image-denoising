import sys
import os
import argparse
import multiprocessing as mp
import time
import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.run import RunData, RunResult, ParameterSpace
from core.denoiser import DenoiserRunParamsString
from evaluation.metric import MetricFactory
from evaluation.thresholds import ThresholdFactory
from evaluation.search import SearchFactory
from evaluation.denoiser import DenoiserRunParams
from evaluation.denoiser_factory import DenoiserFactory
from evaluation.image_loader import ImageLoaderFactory
from utils.versioning import get_version
from utils.serialisation import save, load, print_obj
from utils.image import set_base_path
from utils.factory import unpack_list_config
from utils.array import split_partition_array

class Progress:
    def __init__(self, fn):
        self.callback = fn
    def update(self, current, total, result):
        self.callback(current, total, result)

class Run:
    def __init__(self, parameterSpace, cores = 1, monitoringFn=lambda n,d,r: None, imageBase = '', forceParallel = False):
        self.parameterSpace = parameterSpace
        self.progress = Progress(monitoringFn)
        self.cores = max(1, cores)
        self.runsCompleted = 0
        self.totalRuns = 0
        self.runs = []
        self.version = get_version().to_dict()
        self.imageBase = imageBase
        self.forceParallel = forceParallel

    @staticmethod
    def _task(dp, imageBase):
        set_base_path(imageBase)
        pairImage = dp.pairImage
        iteration = dp.iterations
        sample = dp.sample
        imageLoaderMethod = ImageLoaderFactory.create(dp.imageLoader)
        metricMethod = MetricFactory.create(dp.metric)
        thresholdMethod = ThresholdFactory.create(dp.thresholding)
        searchMethod = SearchFactory.create(dp.search)
        denoiserMethod = DenoiserFactory.create(dp.denoiser)
        denoiserParams = DenoiserRunParams((pairImage[0], pairImage[1]), imageLoaderMethod, metricMethod, thresholdMethod, searchMethod, iteration, denoiserMethod, sample)
        try:
            start = time.perf_counter_ns()
            run = denoiserMethod.run(denoiserParams, dp)
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
            denoiserConfigs = unpack_list_config(p.denoisers)
            searchConfigs = unpack_list_config(p.searchMethods)
            
            # Temporary ternary conditional below, samples should be mandatory
            samples = p.samples if hasattr(p, 'samples') else ParameterSpace().samples
            for denoiserConfig in denoiserConfigs:
                for imageLoader in p.imageLoaders:
                    for img in p.images:
                        refImage = img[0]
                        images = img[1]
                        for image in images:
                            for metric in p.metrics:
                                for threshold in p.thresholds:
                                    for searchConfig in searchConfigs:
                                        for iteration in p.iterations:
                                            for sample in range(samples):
                                                denoiserParamsString = DenoiserRunParamsString(len(denParams), p.name, (refImage, image), imageLoader, metric, threshold, searchConfig, iteration, denoiserConfig, sample)
                                                denParams.append(denoiserParamsString)
        return denParams
    
    def run(self, split, dp = None):
        denParams = Run.get_denoiser_params(self.parameterSpace) if dp is None else dp
        self.totalRuns = len(denParams)
        
        # Run only a small partition
        denParams = split_partition_array(denParams, *split)

        # distribute tasks using multiprocessing
        if self.forceParallel == False and self.cores == 1:
            for denoiserParams in denParams:
                rResult = Run._task(denoiserParams, self.imageBase)
                self.runs.append(rResult)
                self._update(rResult)
        else:
            asyncResults = []
            with mp.Pool(processes=min(self.cores, len(denParams)), maxtasksperchild=1) as pool:
                asyncResults = list(map(lambda dp: pool.apply_async(Run._task, (dp, self.imageBase), callback=self._update), denParams))
                pool.close()
                pool.join()
            for asyncResult in asyncResults:
                if asyncResult.successful():
                    self.runs.append(asyncResult.get())
            #self.runs = list(map(lambda x: x.get(), asyncResults))

def main():
    versionString = get_version().to_string()
    print(versionString)
    parser = argparse.ArgumentParser(description=f'Evaluates denoising using the parameter space provided in the input json file.\n{versionString}')
    parser.add_argument('--config', default='config.json', help='File path to the JSON ParameterSpace list')
    parser.add_argument('--result', default='result.json', help='Where to save the JSON Run object')
    parser.add_argument('--image-base', default='', help='Base path for the images to load')
    parser.add_argument('--temp', default='temp.json', help='Where to save intermediate JSON Run objects')
    parser.add_argument('--cores', default=0, type=int, help='Number of cores to use. 0 uses maximum')
    parser.add_argument('--missing-only', default=False, action='store_true', help='Used to run only the missing runs found in the results')
    parser.add_argument('--force-parallel', default=False, action='store_true', help='Force using python multiprocessing when 1 core is selected')
    parser.add_argument('--missing-result', default='', help='Where to save the JSON Run object for missing-only option.')
    parser.add_argument('--split', default='1,0,1', help='Splits the workload. Enter a string having format total,start,length')
    args = parser.parse_args()

    configPath = args.config
    resultPath = args.result
    missingResultPath = args.missing_result if args.missing_result else resultPath
    tempPath = args.temp
    cores = args.cores if args.cores > 0 and args.cores <= mp.cpu_count() else mp.cpu_count()
    split = tuple(map(int, args.split.split(',')))

    bar = tqdm.tqdm()
    def update(n, d, result):
        save(tempPath, result, write_mode='a')
        bar.total = d
        bar.update(1)

    if args.missing_only:
        print(f'Computing only missing runs from \'{resultPath}\'. Saving all results back to \'{missingResultPath}\'. Max cores: {cores}')
        runData = load(resultPath)
        dp = Run.get_denoiser_params(runData.parameterSpace)
        missing_ids = sorted({p.id for p in dp} - {r.denoiserParams.id for r in runData.runs})
        missing_runs = [dp[m] for m in missing_ids]
        if missing_runs:
            run = Run(runData.parameterSpace, cores, update, args.image_base, args.force_parallel)
            run.run(split, missing_runs)
            runData.runs.extend(run.runs)
            runData.runs = sorted(runData.runs, key=lambda r: r.denoiserParams.id)
            save(missingResultPath, runData)
    else:
        print(f'Reading ParameterSpace from \'{configPath}\' and writing result to \'{resultPath}\'. Max cores: {cores}')
        parameterSpace = load(configPath)
        run = Run(parameterSpace, cores, update, args.image_base, args.force_parallel)
        run.run(split)
        runData = RunData(run.parameterSpace, run.cores, run.totalRuns, run.runs, run.version)
        save(resultPath, runData)
        #save(f'{resultPath}.norefs.json', runData, False)
    
    bar.close()


# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    mp.set_start_method('spawn')
    main()
