from typing import List, Tuple, Dict
from pprint import pprint
from itertools import combinations
import time
from pprint import pprint

from arbitre_gitlab.hitman.hitman import HC, HitmanReferee

from actionChooser import ActionChooser
from aliases import Orientation, Information, Position, OBJECTS_INDEX
from utils import createMap, howManyUnknown, isInformationAlreadyKnown, updateMap, isMapComplete, updateSolutionMap, fromHCDirectionToOrientation, getVisionsFromStatus

def addTurnInfo(status, heardMap, seenMap, map):
    visions = getVisionsFromStatus(status["vision"])
    # print("visions", visions)
    for vision in visions: 
        if (not isInformationAlreadyKnown(map, vision)):
            map = updateMap(map, [vision])

    if status["is_in_guard_range"]:
        seenInfo = 1
    else:
        seenInfo = 0
    if (not isInformationAlreadyKnown(seenMap, (status["position"][0], status["position"][1], seenInfo))):
        seenMap = updateMap(seenMap, [(status["position"][0], status["position"][1], seenInfo)])

    heardInfo: Information = [status["position"][0], status["position"][1], status["hear"]]
    if (not isInformationAlreadyKnown(heardMap, heardInfo)):
        heardMap = updateMap(heardMap, [heardInfo])
    # printMaps([map, heardMap])
    return

def fromHCDirectionToOrientation(direction: HC) -> Orientation:
    if direction == HC.N:
        return "N"
    elif direction == HC.S:
        return "S"
    elif direction == HC.E:
        return "E"
    elif direction == HC.W:
        return "W"
    raise Exception("Unknown direction")

def phase1(referee: HitmanReferee):
    start_time = time.time()

    status = referee.start_phase1()
    # pprint(status)

    n_col = status['n']
    n_lig = status['m']

    actionChooser = ActionChooser(n_col, n_lig)

    map = createMap(n_col, n_lig)
    solutionMap: Dict[Tuple[int, int], HC] = {} 
    heardMap = createMap(n_col, n_lig)
    seenMap = createMap(n_col, n_lig)
    
    map[0][0] = OBJECTS_INDEX['empty']
    updateSolutionMap(solutionMap, [((0, 0), HC.EMPTY)])
    addTurnInfo(status, heardMap, seenMap, map)
    updateSolutionMap(solutionMap, status["vision"])

    MAX = 100
    count = 0
    actions = []
    sat_bonus = 1

    while count < MAX and not isMapComplete(map):
        print("------------------")

        orientation = fromHCDirectionToOrientation(status["orientation"])
        position: Position = [status["position"][0], status["position"][1], orientation]
        print("position: ", position)

        sat_info = (map, heardMap, seenMap, n_col, n_lig, sat_bonus)
        action = actionChooser.choose(map, position, sat_info)

        

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

        addTurnInfo(status, heardMap, seenMap, map)
        updateSolutionMap(solutionMap, status["vision"])
        count += 1

    print("count: ", count)
    # pprint(status)


    # print("Carte connue : \n")
    pprint(map)
    end_time = time.time()
    print("total time: ", end_time - start_time)
    # pprint(solutionMap)
    # pprint(actions)
    print("is good solution for referee....", end=" ")
    print(referee.send_content(solutionMap))
    print("end phase1....")
    pprint(referee.end_phase1())
    return map, end_time - start_time, status["penalties"]

def findObject(map, object):
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] == object:
                return (j, i)
    return None

def isInCase(position, goal):
    if (position[0], position[1]) == (goal[0], goal[1]):
        return True
    return False

def goToGoal(actionChooser: ActionChooser, referee: HitmanReferee, map, startPosition, goal, position: Position, status, MAX, hasObjects: dict[str, bool]):
    count = 0
    actions = []
    while count < MAX and not isInCase(position, goal):
        print("------------------")        

        action = actionChooser.choose_phase2(map, position, goal, hasObjects["hasRope"], hasObjects["hasCostume"], hasObjects["wearCostume"])

        # all actions 
        if action == 1:
            actions.append(('move', position))
            status = referee.move()
        elif action == 2:
            actions.append(("turn 90", position))
            status = referee.turn_clockwise()
        elif action == 3:
            actions.append(("turn -90", position))
            status = referee.turn_anti_clockwise()
        elif action == 4:
            actions.append(("neutralize_guard", position))
            status = referee.neutralize_guard()
            # la position du garde devient vide
            visions = status["vision"]
            map[visions[0][0][1]][visions[0][0][0]] = OBJECTS_INDEX['empty']
        elif action == 5:
            actions.append(("neutralize_civil", position))
            status = referee.neutralize_civil()
            # case becomes empty
            visions = status["vision"]
            map[visions[0][0][1]][visions[0][0][0]] = OBJECTS_INDEX['empty']
        elif action == 6:
            actions.append(("take_weapon", position))
            # case becomes empty
            status = referee.take_weapon()
            position = (status["position"][0], status["position"][1])
            map[position[1]][position[0]] = OBJECTS_INDEX['empty']

        elif action == 7:
            actions.append(("take_suit", position))
            status = referee.take_suit()
            # case becomes empty
            position = (status["position"][0], status["position"][1])
            map[position[1]][position[0]] = OBJECTS_INDEX['empty']
            hasObjects["hasCostume"] = True
        elif action == 8:
            actions.append(("put_suit", position))
            status = referee.put_on_suit()
            hasObjects["wearCostume"] = True
        else: 
            raise Exception("action not found")

        orientation = fromHCDirectionToOrientation(status["orientation"])
        position = (status["position"][0], status["position"][1], orientation)
        count += 1
    print("count: ", count)
    # pprint(status)
    return status, position

def phase2(referee: HitmanReferee, map):
    start_time = time.time()

    status = referee.start_phase2()
    # pprint(status)
    
    ropePosition = findObject(map, OBJECTS_INDEX['rope'])
    if ropePosition is None:
        raise Exception("No rope found")
    costumePosition = findObject(map, OBJECTS_INDEX['costume'])
    if costumePosition is None:
        raise Exception("No costume found")
    targetPosition = findObject(map, OBJECTS_INDEX['target'])
    if targetPosition is None:
        raise Exception("No target found")

    orientation = fromHCDirectionToOrientation(status["orientation"])
    startPosition: Position = (status["position"][0], status["position"][1], orientation)
    position: Position = startPosition
    # print("ropePosition: ", ropePosition)
    # print("costumePosition: ", costumePosition)
    # print("targetPosition: ", targetPosition)
    # print("startPosition: ", startPosition)

    n_col = status['n']
    n_lig = status['m']

    actionChooser = ActionChooser(n_col, n_lig)

    hasObjects = {
        "hasRope": False,
        "hasCostume": False,
        "wearCostume": False
    }
    status, position = goToGoal(actionChooser, referee, map, startPosition, (ropePosition[0], ropePosition[1]), position, status, 100, hasObjects)

    # print("We are on the rope")
    # print("we take the rope")
    status = referee.take_weapon()
    map[ropePosition[1]][ropePosition[0]] = OBJECTS_INDEX['empty']
    if status["has_weapon"] == False:
        raise Exception("We don't have the rope")
    hasObjects["hasRope"] = True
    # print("we have the rope")
    # print("now go kill the target")

    status, position = goToGoal(actionChooser, referee, map, position, (targetPosition[0], targetPosition[1]), position, status, 100, hasObjects)
    ### then go to the target

    # print("We are on the target")
    ### then kill the target
    # print("we kill the target")
    status = referee.kill_target()
    pprint(status)

    ### then come back to the start position
    status, position = goToGoal(actionChooser, referee, map, position, (startPosition[0], startPosition[1]), position, status, 100, hasObjects)

    end_time = time.time()
    print("total time: ", end_time - start_time)
    # ne fonctionne pas pour le moment car on ne met pas les infos des orientations des civils & gardes
    # pprint(actions)
    print("is good solution for referee....", end=" ")
    pprint(referee.end_phase2())
    return end_time - start_time, status["penalties"]

def main():

    scores_p1 = []
    scores_p2 = []

    for map_int in range(0, 9):

        referee = HitmanReferee(map_int)

        map, time, score = phase1(referee)
        scores_p1.append([map_int, time, score])

        time, score = phase2(referee, map)
        scores_p2.append([map_int, time, score])
    
    print("Scores phase 1 :")
    pprint(scores_p1)
    print("Scores phase 2 :")
    pprint(scores_p2)


if __name__ == "__main__":
    main()