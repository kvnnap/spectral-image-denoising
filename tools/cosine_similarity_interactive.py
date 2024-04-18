import sys
import os
import argparse
from numpy import dot
from numpy.linalg import norm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.versioning import get_version
from utils.serialisation import load
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
    print(f'{similarity} -- {to_string_obj(run.denoiserParams)}')
    

def main():
    versionString = get_version().to_string()
    parser = argparse.ArgumentParser(description=f'Fix MSE score.\n{versionString}')
    parser.add_argument('--result', default='result.json', help='Result input to calculate cosine similarity on')
    args, unknown = parser.parse_known_args()

    resultPath = args.result

    print('Loading result')
    runData = load(resultPath)

    print('Grouping by denoiser_coeff')
    denDict = {}
    for run in runData.runs:
        if not run.denoiserParams.imageLoader.startswith('gray'):
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
    # Build list
    cosList = []
    for id1, cosD1 in cosDict.items():
        for id2, cosSim in cosD1.items():
            cosList.append((int(id1), int(id2), cosSim))
    cosList = sorted(cosList, reverse=True, key=lambda x: x[2])
    simpleView = 1

    while True:
        command = input("Enter a command (simple/query/list/show/quit): ")
        if command.lower() == 'quit':
            print("Exiting program.")
            return
        
        rData = None if simpleView else runData

        try:
            cSplit = command.split()
            if cSplit[0] == 'simple':
                simpleView = int(cSplit[1])

            elif cSplit[0] == 'query':
                id = int(cSplit[1])
                numItems = 10
                if len(cSplit) > 2:
                    numItems = int(cSplit[2])

                if id not in cosDict:
                    print(f'run id: {id} not found')
                    continue

                run = cosDict[id]
                sortedRuns = sorted(run.items(), reverse=True, key=lambda x: x[1])
                show_details(rData, id)
                # Print the sorted key-value pairs
                for otherRunId, value in sortedRuns[:numItems]:
                    # print((otherRunId, value))
                    show_details(rData, otherRunId, value)

            elif cSplit[0] == 'show':
                s1 = int(cSplit[1])
                s2 = int(cSplit[2])
                exists = s1 in cosDict and s2 in cosDict[s1]
                if exists:
                    # print((s1, cosDict[s1][s2]))
                    show_details(rData, s2, cosDict[s1][s2])
                else:
                    print(f'{s1} does not associate with {s2}')

            elif cSplit[0] == 'list':
                numItems = 10
                if len(cSplit) > 1:
                    numItems = int(cSplit[1])
                startIndex = 0
                if len(cSplit) > 2:
                    startIndex = int(cSplit[2])
                for s1, s2, cosScore in cosList[startIndex:startIndex+numItems]:
                    print((s1, s2, cosScore))
                    if not simpleView:
                        show_details(rData, s2, cosDict[s1][s2])
            else:
                print('Help')
                print('simple - Enables simple view (default 1)')
                print('query id [num] - Queries the first num highest scores for run id')
                print('list [num] [start_index] - lists num top scores globally. start_index skips scores')
                print('show id1 id2 - shows the score for the pair id1,id2')
                
        except Exception as e:
            print(e)
            continue


# The following code block will only execute if this script is run directly,
# not if it's imported as a module in another script.
if __name__ == "__main__":
    main()

