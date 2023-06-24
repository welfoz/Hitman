from typing import List, Tuple, Dict
from pprint import pprint
import time
from pprint import pprint

from arbitre_gitlab.hitman.hitman import HC, HitmanReferee
from src.actionChooser import ActionChooser
from src.aliases import Position, OBJECTS_INDEX
from src.utils import createMap, howManyUnknown, isMapComplete, updateSolutionMap, fromHCDirectionToOrientation, addTurnInfo, fromHCDirectionToOrientation, findObject

SAT_BONUS = 1

def goToGoal(actionChooser: ActionChooser, referee: HitmanReferee, map, startPosition, position: Position, status, hasObjects: dict[str, bool], targetKilled, ropePosition, targetPosition):
    actions = []
    print("------------------")        

    actions_result = actionChooser.choose_phase2(map, position, hasObjects["hasRope"], hasObjects["hasCostume"], hasObjects["wearCostume"], targetKilled, ropePosition, targetPosition)

    for action in actions_result:
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
        elif action == 9:
            actions.append(("kill_target", position))
            status = referee.kill_target()
        else: 
            raise Exception("action not found")
        if status["status"] != "OK":
            pprint(status)
            print(action)
            raise Exception("invalid move")

    # pprint(status)
    return status, position

def phase1(referee: HitmanReferee):
    start_time = time.time()

    status = referee.start_phase1()

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

    MAX = 100000
    count = 0
    actions = []

    while count < MAX and not isMapComplete(map):
        print("------------------")

        orientation = fromHCDirectionToOrientation(status["orientation"])
        position: Position = [status["position"][0], status["position"][1], orientation]
        print("position: ", position)

        sat_info = (map, heardMap, seenMap, n_col, n_lig, SAT_BONUS)
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

        addTurnInfo(status, heardMap, seenMap, map)
        updateSolutionMap(solutionMap, status["vision"])
        count += 1

    print("count: ", count)
    pprint(map)
    end_time = time.time()
    print("total time: ", end_time - start_time)
    print("is good solution for referee....", end=" ")
    print(referee.send_content(solutionMap))
    print("end phase1....")
    pprint(referee.end_phase1())
    return map, end_time - start_time, status["penalties"]

def phase2(referee: HitmanReferee, map):
    start_time = time.time()

    status = referee.start_phase2()
    
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

    n_col = status['n']
    n_lig = status['m']

    actionChooser = ActionChooser(n_col, n_lig)

    hasObjects = {
        "hasRope": False,
        "hasCostume": False,
        "wearCostume": False
    }
    targetKilled = False
    status, position = goToGoal(actionChooser, referee, map, startPosition, position, status, hasObjects, targetKilled, ropePosition, targetPosition)

    end_time = time.time()
    print("total time: ", end_time - start_time)
    print("is good solution for referee....", end=" ")
    pprint(referee.end_phase2())
    return end_time - start_time, status["penalties"]

def main():
    # INSTALLATION : attention, l'éxécutable gophersat doit être dans /gophersat/

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