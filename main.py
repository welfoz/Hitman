from typing import List, Tuple, Dict
from pprint import pprint
from itertools import combinations
import time

from arbitre_gitlab.hitman.hitman import HC, HitmanReferee

from actionChooser import ActionChooser, createMap, isInformationAlreadyKnown, updateMap
from aliases import  Literal, ClauseBase, Orientation, Information, Position, OBJECTS_INDEX
from utils import createMap, howManyUnknown, isInformationAlreadyKnown, updateMap, isMapComplete, updateSolutionMap, fromHCDirectionToOrientation, getVisionsFromStatus
from satUtils import addInfoListening, addInfoIsInGuardRange, addInfoVision, is_position_safe, generateInitialClauses, is_position_safe_opti

# def addTurnInfo(status, heardMap, map, clauses):
def addTurnInfo(status, heardMap, map):
    # print()
    visions = getVisionsFromStatus(status["vision"])
    # print("visions", visions)

    for vision in visions: 
        if (not isInformationAlreadyKnown(map, vision)):
            # print("add info vision")
            # print(len(clauses))
            # clauses += addInfoVision(status['n'], status['m'], vision)
            # print(len(clauses))
            map = updateMap(map, [vision])

    # if status['is_in_guard_range']:
    #     clauses += addInfoIsInGuardRange(status['n'], status['m'], status['position'])

    heardInfo: Information = [status["position"][0], status["position"][1], status["hear"]]
    if (not isInformationAlreadyKnown(heardMap, heardInfo)):
        # print("add info listening")
        # print(len(clauses))
        # clauses += addInfoListening(status['n'], status['m'], status['position'], status['hear'], map)
        # print(len(clauses))
        heardMap = updateMap(heardMap, [heardInfo])

    print()
    
    # printMaps([map, heardMap])
    # input("Press Enter to continue...")
    return

def phase1(referee):
    start_time = time.time()

    status = referee.start_phase1()
    pprint(status)

    n_col = status['n']
    n_lig = status['m']

    actionChooser = ActionChooser(n_col, n_lig)

    map = createMap(n_col, n_lig)
    solutionMap: Dict[Tuple[int, int], HC] = {} 
    heardMap = createMap(n_col, n_lig)

    # clauses = generateInitialClauses(n_col, n_lig, status['guard_count'], status['civil_count'])
    
    map[0][0] = OBJECTS_INDEX['empty']
    updateSolutionMap(solutionMap, [((0, 0), HC.EMPTY)])

    # addTurnInfo(status, heardMap, map, clauses)
    addTurnInfo(status, heardMap, map)
    updateSolutionMap(solutionMap, status["vision"])

    MAX = 100
    count = 0
    actions = []

    while count < MAX and not isMapComplete(map):
        print("------------------")

        orientation = fromHCDirectionToOrientation(status["orientation"])
        position: Position = [status["position"][0], status["position"][1], orientation]
        print("position: ", position)

        # print(len(clauses))
        print(status["hear"])
        print(is_position_safe_opti(position, map, heardMap, n_col, n_lig))
        # safe  = is_position_safe(position, map, clauses, n_col, n_lig)
        # print(safe)

        action = actionChooser.choose(map, position)

        unknown = howManyUnknown(map)
        if action == 1:
            actions.append(('move', position, unknown))
            status = referee.move()
        elif action == 2:
            actions.append(("turn 90", position, unknown))
            status = referee.turn_clockwise()
        elif action == 3:
            actions.append(("turn -90", position, unknown))
            status = referee.turn_anti_clockwise()

        # pprint({
        #     "vision": status['vision'],
        #     "hear": status['hear'],
        #     "position": status['position'],
        #     "orientation": status['orientation'],
        #     "is_in_guard_range": status['is_in_guard_range'],
        #     "penalties": status['penalties'],
        #     "status": status['status']
        # })

        # addTurnInfo(status, heardMap, map, clauses)
        addTurnInfo(status, heardMap, map)
        updateSolutionMap(solutionMap, status["vision"])
        count += 1
    print("count: ", count)
    pprint(status)


    # print("Carte connue : \n")
    # print(solveur(clauses, dimension))
    # map_info = solutionToMap(solveur(clauses, dimension)[1], status['n'], status['m'])
    pprint(map)
    end_time = time.time()
    print("total time: ", end_time - start_time)
    pprint(solutionMap)
    pprint(actions)
    print("is good solution for referee....", end=" ")
    print(referee.send_content(solutionMap))

def main():

    referee = HitmanReferee()
    map = phase1(referee)

    """
    phase 2

    first goal: 
    go to the rope, take it then go to the target in a minimum of actions and kill it
    come back to the start position

    second goal:
    same in a minimum of penalties (include guards seen, rope, costume...)
    come back to the start position
    """


if __name__ == "__main__":
    main()