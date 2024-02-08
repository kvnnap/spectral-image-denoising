import sys
import os
import argparse
import multiprocessing as mp
import jsonpickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.run import RunData
from evaluation.run import Run
from utils.versioning import get_version
from utils.serialisation import save, load

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Recoveres crashed run data from a temp file.\n{versionString}')
    parser.add_argument('--config', default='config.json', help='File path to the JSON ParameterSpace list')
    parser.add_argument('--result', default='result.json', help='Where to save the JSON Run object')
    parser.add_argument('--temp', default='temp.json', help='Where to load intermediate JSON Run objects from')
    parser.add_argument('--cores', default=0, type=int, help='Number of cores to use. 0 uses maximum - just to set it in recovered file')
    args = parser.parse_args()

    configPath = args.config
    resultPath = args.result
    tempPath = args.temp
    cores = args.cores if args.cores > 0 and args.cores <= mp.cpu_count() else mp.cpu_count()

    parameterSpace = load(configPath)
    run = Run(parameterSpace, cores)
    run.totalRuns = len(Run.get_denoiser_params(parameterSpace))

    # Read the content of the input file
    content = ''
    with open(tempPath, 'r') as input_file:
        content = input_file.read()

    # Split the content at '}{', add commas, and enclose it in square brackets to create a valid JSON array
    #modified_content = '[' + content.replace('}{', '},{') + ']'

    # Need to do the following because temp.json may generate reference data.. 
    mod = content.split('}{')
    modLength = len(mod)
    if modLength > 1:
        mod[0] += '}'
        mod[-1] = '{' + mod[-1]
    for i, obj in enumerate(mod):
        if i != 0 and i != modLength - 1:
            obj = '{' + obj + '}'
        run.runs.append(jsonpickle.decode(obj))

    #run.runs = jsonpickle.decode(modified_content)
    runData = RunData(run.parameterSpace, run.cores, run.totalRuns, run.runs, run.version)

    save(resultPath, runData)
    save(f'{resultPath}.norefs.json', runData, False)

    print(f'Recovered {len(run.runs)} results')


# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

