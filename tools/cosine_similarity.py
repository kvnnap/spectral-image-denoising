import sys
import os
import argparse
import numpy as np
from numpy import dot
from numpy.linalg import norm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import save, load
from visualisation.result_image_processor import ResultImageProcessor
from utils.serialisation import to_string_obj

def get_run_from__row_id(runData, runId):
    return next((x for x in runData.runs if x.denoiserParams.id == runId), None)

def show_details(runData, runId, similarity = 1.0):
    runId = int(runId)
    if not runData:
        print((runId, similarity))
        return

    # Find run by id
    run = get_run_from__row_id(runData, runId)
    # scores = ResultImageProcessor(run).compute_score()
    print(f'{similarity} -- {to_string_obj(run.denoiserParams)}')
    

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Fix MSE score.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='Result input to calculate cosine similarity on')
    parser.add_argument('--matrix', default='cosine_similarity.json', help='Output file or input file')
    parser.add_argument('--gen-matrix', action='store_true', help='Are we generating the matrix?')
    parser.add_argument('--show-run-info', action='store_true', help='Show details')
    parser.add_argument('--query', type=int, help='We are querying the matrix. The run id to query')
    parser.add_argument('--similarity', help='two integers, colon seperated. id1:id2')
    parser.add_argument('--num-items', type=int, default=10, help='The number of items to show')
    args = parser.parse_args()

    resultPath = args.result
    outputPath = args.matrix
    genMatrix = args.gen_matrix
    #genMatrix = True
    query = args.query
    similarity = args.similarity.split(':') if args.similarity else args.similarity
    numItems = args.num_items
    showRunInfo = args.show_run_info

    if genMatrix:

        print('Loading result')
        runData = load(resultPath)

        print('Grouping by denoiser_coeff')
        denDict = {}
        for run in runData.runs:
            if run.denoiserParams.imageLoader not in ['gray', 'gray_tm']:
                continue
            # Categorise depending on denoiser_coeff
            key = run.denoiserParams.get_value('denoiser_coeff')
            if key not in denDict:
                denDict[key] = []    
            denDict[key].append(run)

        print('Generating cosine similarity matrix')
        # Gen matrix
        cosDict = {}
        cosList = []
        for den, runs in denDict.items():
            for run in runs:
                # Grab this run and compare with other runs
                dp1 = run.denoiserParams
                id1 = dp1.id
                cosDict[run.denoiserParams.id] = {}
                for otherRun in runs:
                    dp2 = otherRun.denoiserParams

                    # Ignore same scenes
                    if (dp1.pairImage[0] == dp2.pairImage[0]):
                        continue

                    # Different thresholding methods do not make sense
                    if (dp1.thresholding != dp2.thresholding):
                        continue

                    x1 = run.denoiserResult.x
                    x2 = otherRun.denoiserResult.x

                    # Vectors of different length signify images of different resolution
                    if len(x1) != len(x2):
                        continue

                    nx1 = norm(x1)
                    nx2 = norm(x2)
                    if nx1 > 0 and nx2 > 0:
                        # Perform cos similiarity
                        id2 = dp2.id
                        cos_sim = dot(x1, x2) / (nx1 * nx2)
                        cosDict[id1][id2] = cos_sim.item()
                        cosList.append((id1, id2, cos_sim.item()))

        print('Saving data')
        save(outputPath, cosDict)
        #save(f'{outputPath}.norefs.json', runData, False)
    else:
        # queries
        print('Loading matrix')
        cosDict = load(outputPath)
        runData = None

        if showRunInfo:
            print('Loading result for extra details')
            runData = load(resultPath)

        # Build list
        cosList = []
        for id1, cosD1 in cosDict.items():
            for id2, cosSim in cosD1.items():
                cosList.append((int(id1), int(id2), cosSim))
        cosList = sorted(cosList, reverse=True, key=lambda x: x[2])

        if query != None:
            run = cosDict[str(query)]
            sortedRuns = sorted(run.items(), reverse=True, key=lambda x: x[1])
            show_details(runData, query)
            # Print the sorted key-value pairs
            for otherRunId, value in sortedRuns[:numItems]:
                # print((otherRunId, value))
                show_details(runData, otherRunId, value)

        if similarity:
            s1 = similarity[0]
            s2 = similarity[1]
            exists = s1 in cosDict and s2 in cosDict[s1]
            if exists:
                # print((s1, cosDict[s1][s2]))
                show_details(runData, s2, cosDict[s1][s2])
            else:
                print(f'{s1} does not associate with {s2}')
            


# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

