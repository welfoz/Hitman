from typing import List, Tuple, Dict
from pprint import pprint
from itertools import combinations
import time

from arbitre_gitlab.hitman.hitman import HC, HitmanReferee

from actionChooser import ActionChooser, createMap, isInformationAlreadyKnown, updateMap
from aliases import  Literal, ClauseBase, Orientation, Information, Position, OBJECTS_INDEX
from utils import createMap, howManyUnknown, isInformationAlreadyKnown, updateMap, clausesToDimacs, exec_gophersat, isMapComplete, write_dimacs_file

# generation des types possibles pour une case
def generateTypesGrid(n_col : int, n_lig : int) -> ClauseBase:
    objectNumber = len(OBJECTS_INDEX)
    clauses = []
    for i in range(n_col):
        for j in range(n_lig):
            literals = []
            for k in range(objectNumber):
                literals.append(i * n_lig * objectNumber + j * objectNumber + k + 1)
            clauses += uniqueX(literals, 1)
    return clauses

# generation des clauses pour un nombre donne d'ojects dans la carte
def generateClausesForObject(n_col : int, n_lig : int, n_object: int, object_index: int) -> ClauseBase:
    litterals = []
    for i in range(n_col):
        for j in range(n_lig):
            litterals.append(i * n_lig * 7 + j * 7 + object_index)
    r = uniqueX(litterals, n_object)
    #print("Clauses pour " + str(n_object) + " " + list(OBJECTS_INDEX.keys())[list(OBJECTS_INDEX.values()).index(object_index)] + " :")
    #print(r)
    return r

def HCInfoToObjectIndex(value : int) -> int:
    if value in range(HC.GUARD_N._value_, HC.GUARD_W._value_ + 1):
        return OBJECTS_INDEX['guard'][0]
    if value in range(HC.CIVIL_N._value_, HC.CIVIL_W._value_ + 1):
        return OBJECTS_INDEX['civil'][0]
    if value == HC.EMPTY._value_:
        return OBJECTS_INDEX['empty']
    if value == HC.WALL._value_:
        return OBJECTS_INDEX['wall']
    if value == HC.TARGET._value_:
        return OBJECTS_INDEX['target']
    if value == HC.SUIT._value_:
        return OBJECTS_INDEX['costume']
    if value == HC.PIANO_WIRE._value_:
        return OBJECTS_INDEX['rope']

def HCInfoToObjectIndexFull(value : int) -> int:
    # if value in range(HC.GUARD_N._value_, HC.GUARD_W._value_ + 1):
    if value == HC.GUARD_N._value_:
        return OBJECTS_INDEX['guard'][1]
    if value == HC.GUARD_S._value_:
        return OBJECTS_INDEX['guard'][2]
    if value == HC.GUARD_E._value_:
        return OBJECTS_INDEX['guard'][3]
    if value == HC.GUARD_W._value_:
        return OBJECTS_INDEX['guard'][4]
    if value == HC.CIVIL_N._value_:
        return OBJECTS_INDEX['civil'][1]
    if value == HC.CIVIL_S._value_:
        return OBJECTS_INDEX['civil'][2]
    if value == HC.CIVIL_E._value_:
        return OBJECTS_INDEX['civil'][3]
    if value == HC.CIVIL_W._value_:
        return OBJECTS_INDEX['civil'][4]
    if value == HC.EMPTY._value_:
        return OBJECTS_INDEX['empty']
    if value == HC.WALL._value_:
        return OBJECTS_INDEX['wall']
    if value == HC.TARGET._value_:
        return OBJECTS_INDEX['target']
    if value == HC.SUIT._value_:
        return OBJECTS_INDEX['costume']
    if value == HC.PIANO_WIRE._value_:
        return OBJECTS_INDEX['rope']

def addInfoVision(n_col : int, n_lig : int, info_vision : Information) -> ClauseBase:
    # print("Info vision : " + str(info_vision))
    x = info_vision[0]
    y = info_vision[1]
    value = info_vision[2]
    # print("Clauses pour les infos de vision : ")
    # print(result)
    return [[x * n_lig * 7 + y * 7 + value]]

# est ce juste pour nb_heard = 0 ?
def addInfoListening(n_col : int, n_lig : int, position : Tuple, nb_heard : int, map) -> ClauseBase:
    x = position[0]
    y = position[1]
    litterals = []
    guardsOrCivils = nb_heard
    #pour toutes les cases autour
    for i in range(x-2, x+3):
        for j in range(y-2, y+3):
            if i < 0 or i >= n_col or j < 0 or j >= n_lig:
                continue
            if map[j][i] != -1:
                if map[j][i] == HCInfoToObjectIndex(HC.GUARD_N.value):
                    guardsOrCivils -= 1
                if map[j][i] == HCInfoToObjectIndex(HC.CIVIL_N.value):
                    guardsOrCivils -= 1
                # print("Case deja connue", i, j, map[j][i], guardsOrCivils)
                continue
            
            litterals.append(i * n_lig * 7 + j * 7 + OBJECTS_INDEX['guard'][0])
            litterals.append(i * n_lig * 7 + j * 7 + OBJECTS_INDEX['civil'][0])
    if nb_heard > 4:
        return atLeast(guardsOrCivils, litterals)
    return uniqueX(litterals, guardsOrCivils)

# prise en compte du is_in_guard_range
def addInfoIsInGuardRange(n_col : int, n_lig : int, position : Tuple) -> ClauseBase:
    x = position[0]
    y = position[1]
    litterals = []
    # cases horizontales
    for i in range(x-2, x+3):
        if i < 0 or i >= n_col:
            continue
        litterals.append(i * n_lig * 7 + y * 7 + OBJECTS_INDEX['guard'][0])
    # cases verticales
    for j in range(y-2, y+3):
        if j < 0 or j >= n_lig:
            continue
        litterals.append(x * n_lig * 7 + j * 7 + OBJECTS_INDEX['guard'][0])
    # print(litterals)
    return atLeast(1, litterals)

def solveur(clauses: ClauseBase, dimension : int) -> Tuple[bool, List[int]]:
    filename = "temp.cnf"
    dimacs = clausesToDimacs(clauses, dimension)
    write_dimacs_file("\n".join(dimacs), filename)
    return exec_gophersat(filename)

def isSolutionUnique(clauses: ClauseBase, dimension : int) -> bool:
    start_time = time.time()
    sol = solveur(clauses, dimension)
    # print(sol)
    # solutionToMap(sol[1], 3, 3)
    if not sol[0]: return False

    # print("Solution : \n")
    # print(sol[1])
    sol2 = solveur(clauses + [[-x for x in sol[1]]], dimension)
    end_time = time.time()
    print("solveur time: ", end_time - start_time)
    if sol2[0]:
        # print("Pas d'unicite")
        return False
    else:
        # print("Solution unique")
        return True

def atMost(atMostNumber: int, literals: List[Literal]) -> ClauseBase:
    """
    Generate clauses to express that at most atMostNumber literals in literals are true
    @param atMostNumber: the number of literals that are allowed to be true
    @param literals: the literals that are concerned by the constraint
    """
    clauses = []
    for comb in combinations(literals, atMostNumber + 1):
        clauses.append([-l for l in comb])
    return clauses
    
def atLeast(atLeastNumber: int, literals: List[Literal]) -> ClauseBase:
    """
    Generate clauses to express that at least atLeastNumber literals in literals are true
    @param atLeastNumber: the number of literals that are required to be true
    @param literals: the literals that are concerned by the constraint
    """
    clauses = []
    for comb in combinations(literals, len(literals) - atLeastNumber + 1):
        clauses.append([l for l in comb])
    return clauses

def uniqueX(literals: List[Literal], x: int) -> ClauseBase:
    """
    Generate clauses to express that exactly x literals in literals are true
    @param literals: the literals that are concerned by the constraint
    @param x: the number of literals that are required to be true
    """
    clauses = []

    if x == 0:
        return atMost(x, literals)
    
    # at least x, least x-1, x-2, ... 1
    for i in range(1, x):
        clauses += atLeast(i, literals)

    clauses += atLeast(x, literals) + atMost(x, literals)
    return clauses

# calcule la proba de chaque littéral dans les solutions du solveur
def probaLitteral(clauses: ClauseBase, dimension : int) -> List[float]:
    proba = [0] * dimension
    n = 0
    sol = solveur(clauses, dimension)
    while sol[0] & (n < 1001):
        n += 1
        for c in sol[1]:
            if c > 0:
                proba[c-1] += 1
            else:
                proba[-c-1] -= 1
        sol = solveur(clauses + [[-x for x in sol[1]]], dimension)
    return [p/(n) for p in proba]

def getKeyFromValue(obj: Dict[str, int], value: int) -> str:
    for key, v in obj.items():
        if v == value:
            return key
        # check if v is a list
        if isinstance(v, list) and value in v:
            return key

def solutionToMap(solution: List[int], n_col : int, n_lig : int) -> Dict[Tuple[int, int], HC]:
    objectNumber = len(OBJECTS_INDEX)
    map_info: Dict[Tuple[int, int], HC] = {}
    map_info_readable: Dict[Tuple[int, int], HC] = {}

    for i in range(n_col):
        for j in range(n_lig):
            for k in range(objectNumber):
                if solution[i * n_lig * objectNumber + j * objectNumber + k] > 0:
                    map_info_readable[(i, j)] = getKeyFromValue(OBJECTS_INDEX, k + 1)
                    ## need to keep the map with guard N ...
                    map_info[(i, j)] = k + 1
    pprint(map_info_readable)
    return map_info

def getVisionsFromStatus(status_vision: List[Tuple[Tuple[int, int], HC]]) -> List[Information]:
    # print("status vision", status_vision)
    visions = []
    for vision in status_vision:
        visionValue = HCInfoToObjectIndexFull(vision[1].value)
        visions.append([vision[0][0], vision[0][1], visionValue])
    return visions

def updateSolutionMap(solutionMap: Dict[Tuple[int, int], HC], vision: List[Tuple[Tuple[int, int], HC]]) -> Dict[Tuple[int, int], HC]:
    for v in vision:
        solutionMap[(v[0][0], v[0][1])] = v[1]
    return solutionMap

def addTurnInfo(status, heardMap, map, clauses):
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
    pprint(status)

    n_col = status['n']
    n_lig = status['m']

    actionChooser = ActionChooser(n_col, n_lig)

    map = createMap(n_col, n_lig)
    solutionMap: Dict[Tuple[int, int], HC] = {} 
    heardMap = createMap(n_col, n_lig)

    clauses = []
    # clauses += generateTypesGrid(status['n'], status['m'])
    # clauses += generateClausesForObject(status['n'], status['m'], status['guard_count'], OBJECTS_INDEX['guard'][0])
    # clauses += generateClausesForObject(status['n'], status['m'], status['civil_count'], OBJECTS_INDEX['civil'][0])
    # clauses += generateClausesForObject(status['n'], status['m'], 1, OBJECTS_INDEX['target'])
    # clauses += generateClausesForObject(status['n'], status['m'], 1, OBJECTS_INDEX['rope'])
    # clauses += generateClausesForObject(status['n'], status['m'], 1, OBJECTS_INDEX['costume'])
    # print(len(clauses))

    # case 0,0 est vide
    # on est sûr de ca ?
    # clauses.append([(OBJECTS_INDEX['empty'])])
    map[0][0] = OBJECTS_INDEX['empty']
    
    addTurnInfo(status, heardMap, map, clauses)
    updateSolutionMap(solutionMap, [((0, 0), HC.EMPTY)])
    updateSolutionMap(solutionMap, status["vision"])

    dimension = status['n'] * status['m'] * len(OBJECTS_INDEX)
    MAX = 100
    count = 0
    actions = []
    while count < MAX and not isMapComplete(map):
        print("------------------")        

        orientation = fromHCDirectionToOrientation(status["orientation"])
        position: Position = [status["position"][0], status["position"][1], orientation]
        # print("position: ", position)

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
        addTurnInfo(status, heardMap, map, clauses)
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
    # ne fonctionne pas pour le moment car on ne met pas les infos des orientations des civils & gardes
    pprint(solutionMap)
    pprint(actions)
    print("is good solution for referee....", end=" ")
    print(referee.send_content(solutionMap))
    print("end phase1....")
    pprint(referee.end_phase1())
    return map

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

def goToGoal(actionChooser: ActionChooser, referee: HitmanReferee, map, startPosition, goal, position: Position, status, MAX):
    count = 0
    actions = []
    while count < MAX and not isInCase(position, goal):
        print("------------------")        

        action = actionChooser.choose_phase2(map, position, goal)

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
        elif action == 5:
            actions.append(("neutralize_civil", position))
            status = referee.neutralize_civil()
        elif action == 6:
            actions.append(("take_weapon", position))
            status = referee.take_weapon()
        elif action == 7:
            actions.append(("take_suit", position))
            status = referee.take_suit()
        elif action == 8:
            actions.append(("put_on_suit", position))
            status = referee.put_on_suit()
        else: 
            raise Exception("action not found")

        orientation = fromHCDirectionToOrientation(status["orientation"])
        position = (status["position"][0], status["position"][1], orientation)
        count += 1
    print("count: ", count)
    pprint(status)
    return status, position

def phase2(referee: HitmanReferee, map):
    map = [[1, 1, 2, 2, 1, 4, 1], # default map 6*7
            [1, 1, 1, 1, 1, 1, 1],
            [2, 2, 1, 10, 1, 14, 15],
            [3, 2, 1, 1, 1, 12, 1],
            [1, 2, 1, 1, 1, 1, 1],
            [1, 1, 1, 5, 9, 2, 2]]
    start_time = time.time()

    status = referee.start_phase2()
    pprint(status)
    
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
    print("ropePosition: ", ropePosition)
    print("costumePosition: ", costumePosition)
    print("targetPosition: ", targetPosition)
    print("startPosition: ", startPosition)


    n_col = status['n']
    n_lig = status['m']

    actionChooser = ActionChooser(n_col, n_lig)

    status, position = goToGoal(actionChooser, referee, map, startPosition, (ropePosition[0], ropePosition[1]), position, status, 100)

    print("We are on the rope")
    print("we take the rope")
    status = referee.take_weapon()
    # the case becomes empty
    map[ropePosition[1]][ropePosition[0]] = OBJECTS_INDEX['empty']
    if status["has_weapon"] == False:
        raise Exception("We don't have the rope")
    print("we have the rope")

    print("now go kill the target")

    status, position = goToGoal(actionChooser, referee, map, position, (targetPosition[0], targetPosition[1]), position, status, 100)
    ### then go to the target

    print("We are on the target")
    ### then kill the target
    print("we kill the target")
    status = referee.kill_target()
    pprint(status)

    ### then come back to the start position
    status, position = goToGoal(actionChooser, referee, map, position, (startPosition[0], startPosition[1]), position, status, 100)

    end_time = time.time()
    print("total time: ", end_time - start_time)
    # ne fonctionne pas pour le moment car on ne met pas les infos des orientations des civils & gardes
    # pprint(actions)
    print("is good solution for referee....", end=" ")
    pprint(referee.end_phase2())
    return 

def main():
    referee = HitmanReferee()
    # map = phase1(referee)

    """
    phase 2

    first goal: 
    go to the rope, take it then go to the target in a minimum of actions and kill it
    come back to the start position

    second goal:
    same in a minimum of penalties (include guards seen, rope, costume...)
    come back to the start position
    """
    phase2(referee, map)


if __name__ == "__main__":
    main()