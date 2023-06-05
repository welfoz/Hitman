from typing import List, Tuple, Dict
import subprocess
import os
import platform
from enum import Enum
from pprint import pprint
from itertools import combinations

from arbitre_gitlab.hitman.hitman import HC, HitmanReferee, complete_map_example

from stateTree import ActionChoice, createMap, isInformationAlreadyKnown, updateMap
from aliases import  Literal, ClauseBase, Orientation, Information, Position, OBJECTS_INDEX

#### fonctions fournies
def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)

# l'executable gophersat soit etre dans le cwd
def exec_gophersat(
    filename: str, cmd: str = "", encoding: str = "utf8"
) -> Tuple[bool, List[int]]:
    # Vérifier si l'OS est macOS
    if platform.system() == 'Darwin':
        cmd = os.getcwd() + "/gophersat"
    # Vérifier si l'OS est Windows
    if platform.system() == 'Windows':
        cmd = os.getcwd() + "\gophersat\gophersat.exe"

    result = subprocess.run(
        [cmd, filename], capture_output=True, check=True, encoding=encoding
    )
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:-2].split(" ")

    return True, [int(x) for x in model]

def clausesToDimacs(clauses: ClauseBase, dimension: int) -> List[str]:
    # dimacs = "p cnf " + str(pow(dimension, 3)) + ' ' + str(len(clauses)) pas compris pk c'est dim^3
    dimacs = "p cnf " + str(dimension) + ' ' + str(len(clauses))
    result = [dimacs]
    for clause in clauses:
        line = ""
        for literal in clause:
            line += str(literal) + " "
        line += "0"
        result.append(line)
    result.append("")
    return result

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
    sol = solveur(clauses, dimension)
    # print(sol)
    # solutionToMap(sol[1], 3, 3)
    if not sol[0]: return False

    # print("Solution : \n")
    # print(sol[1])
    sol2 = solveur(clauses + [[-x for x in sol[1]]], dimension)
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
    print("status vision", status_vision)
    visions = []
    for vision in status_vision:
        visionValue = HCInfoToObjectIndex(vision[1].value)
        visions.append([vision[0][0], vision[0][1], visionValue])
    return visions

def printMaps(maps, reverse = True):
    print("maps")
    for map in maps:
        if reverse:
            for i in range(len(map) - 1, -1, -1):
                print(map[i])
        else:
            for i in range(len(map)):
                print(map[i])
        print()


def addTurnInfo(status, heardMap, map, clauses):
    print()
    visions = getVisionsFromStatus(status["vision"])
    print("visions", visions)

    for vision in visions: 
        if (not isInformationAlreadyKnown(map, vision)):
            print("add info vision")
            print(len(clauses))
            clauses += addInfoVision(status['n'], status['m'], vision)
            print(len(clauses))
            map = updateMap(map, [vision])

    if status['is_in_guard_range']:
        clauses += addInfoIsInGuardRange(status['n'], status['m'], status['position'])

    heardInfo: Information = [status["position"][0], status["position"][1], status["hear"]]
    if (not isInformationAlreadyKnown(heardMap, heardInfo)):
        print("add info listening")
        print(len(clauses))
        clauses += addInfoListening(status['n'], status['m'], status['position'], status['hear'], map)
        print(len(clauses))
        heardMap = updateMap(heardMap, [heardInfo])

    print()
    
    printMaps([map, heardMap])
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

def main():

    referee = HitmanReferee()
    status = referee.start_phase1()
    pprint(status)

    n_col = status['n']
    n_lig = status['m']

    actionChooser = ActionChoice(n_col, n_lig)

    map = createMap(n_col, n_lig)
    heardMap = createMap(n_col, n_lig)

    clauses = []
    clauses += generateTypesGrid(status['n'], status['m'])
    clauses += generateClausesForObject(status['n'], status['m'], status['guard_count'], OBJECTS_INDEX['guard'][0])
    clauses += generateClausesForObject(status['n'], status['m'], status['civil_count'], OBJECTS_INDEX['civil'][0])
    clauses += generateClausesForObject(status['n'], status['m'], 1, OBJECTS_INDEX['target'])
    clauses += generateClausesForObject(status['n'], status['m'], 1, OBJECTS_INDEX['rope'])
    clauses += generateClausesForObject(status['n'], status['m'], 1, OBJECTS_INDEX['costume'])
    print(len(clauses))

    # case 0,0 est vide
    # on est sûr de ca ?
    clauses.append([(OBJECTS_INDEX['empty'])])
    map[0][0] = OBJECTS_INDEX['empty']
    
    addTurnInfo(status, heardMap, map, clauses)

    dimension = status['n'] * status['m'] * len(OBJECTS_INDEX)
    while not isSolutionUnique(clauses, dimension):
        print()
        print("------------------")        

        orientation = fromHCDirectionToOrientation(status["orientation"])
        position: Position = [status["position"][0], status["position"][1], orientation]
        print("position: ", position)

        action = actionChooser.choose(map, position)

        print("action: ", end="")
        if action == 1:
            print("move")
            status = referee.move()
        elif action == 2:
            print("turn 90")
            status = referee.turn_clockwise()
        elif action == 3:
            print("turn -90")
            status = referee.turn_anti_clockwise()

        pprint({
            "vision": status['vision'],
            "hear": status['hear'],
            "position": status['position'],
            "orientation": status['orientation'],
            "is_in_guard_range": status['is_in_guard_range'],
            "penalties": status['penalties'],
            "status": status['status']
        })
        addTurnInfo(status, heardMap, map, clauses)

    print("Carte connue : \n")
    print(solveur(clauses, dimension))
    map_info = solutionToMap(solveur(clauses, dimension)[1], status['n'], status['m'])
    print("is good solution for referee")
    # ne fonctionne pas pour le moment car on ne met pas les infos des orientations des civils & gardes
    print(referee.send_content(map_info))

if __name__ == "__main__":
    main()