from typing import List, Tuple, Dict
import subprocess
import os
import platform
from enum import Enum
from pprint import pprint
from itertools import combinations

from arbitre_gitlab.hitman.hitman import HC, HitmanReferee, complete_map_example

# alias de types
Grid = List[List[int]] 
PropositionnalVariable = int
Literal = int
Clause = List[Literal]
ClauseBase = List[Clause]
Model = List[Literal]
Action = Enum('Action', ['turn90', 'turn-90', 'move'])
LookingDirection = Enum('LookingDirection', ['nord', 'est', 'sud', 'ouest', 'na'])

OBJECTS_INDEX = {
    'empty': 1,
    'wall': 2,
    'guard': 3,
    'civil': 4,
    'target': 5,
    'rope': 6,
    'costume': 7
}

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
        return OBJECTS_INDEX['guard']
    if value in range(HC.CIVIL_N._value_, HC.CIVIL_W._value_ + 1):
        return OBJECTS_INDEX['civil']
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

        
def addInfoVision(n_col : int, n_lig : int, infos_vision : List) -> ClauseBase:
    result = []
    for info in infos_vision:
        x = info[0][0]
        y = info[0][1]
        typeCase = HCInfoToObjectIndex(info[1].value)
        # print("Infos de la case vue : ")
        # print(f"x : {x}")
        # print(f"y : {y}")
        # print(f"type : {typeCase}")
        result.append([x * n_lig * 7 + y * 7 + typeCase])
    # print("Clauses pour les infos de vision : ")
    # print(result)
    return result

# est ce juste pour nb_heard = 0 ?
def addInfoListening(n_col : int, n_lig : int, position : Tuple, nb_heard : int) -> ClauseBase:
    x = position[0]
    y = position[1]
    litterals = []
    #pour toutes les cases autour
    for i in range(x-2, x+3):
        for j in range(y-2, y+3):
            if i < 0 or i >= n_col or j < 0 or j >= n_lig:
                continue
            litterals.append(i * n_lig * 7 + j * 7 + OBJECTS_INDEX['guard'])
            litterals.append(i * n_lig * 7 + j * 7 + OBJECTS_INDEX['civil'])
    if nb_heard > 4:
        return atLeast(5, litterals)
    return uniqueX(litterals, nb_heard)

def solveur(clauses: ClauseBase, dimension : int) -> Tuple[bool, List[int]]:
    filename = "temp.cnf"
    dimacs = clausesToDimacs(clauses, dimension)
    write_dimacs_file("\n".join(dimacs), filename)
    return exec_gophersat(filename)

def solutionPossible(clauses: ClauseBase, dimension : int) -> bool:
    sol = solveur(clauses, dimension)
    #print(sol)
    return sol[0]

def isSolutionUnique(clauses: ClauseBase, dimension : int) -> bool:
    sol = solveur(clauses, dimension)
    # print(sol)
    solutionToMap(sol[1], 3, 3)
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

def moveChoice(map: Grid, position: Tuple[int, int], lookingDirection: LookingDirection) -> Action:
    """
    todo: 
    - deals with borders -> turn, first Fabien
    - deals with walls
    - deals with guards and civils vision 
    - minimizes the number of actions
    """
    print("move")

def createMap(n_col : int, n_lig : int) -> Grid:
    """
    Create a map of size n_col * n_lig
    @param n_col: number of columns
    @param n_lig: number of lines
    """
    map = []
    for i in range(n_col):
        map.append([])
        for j in range(n_lig):
            map[i].append(0)
    return map

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

def main():

    referee = HitmanReferee()
    status = referee.start_phase1()
    pprint(status)
    # input("Press Enter to continue...")
    clauses = []
    clauses += generateTypesGrid(status['n'], status['m'])
    # print(len(clauses))
    # input("Press Enter to continue...")
    clauses += generateClausesForObject(status['n'], status['m'], status['guard_count'], OBJECTS_INDEX['guard'])
    # print(len(clauses))
    # input("Press Enter to continue...")
    clauses += generateClausesForObject(status['n'], status['m'], status['civil_count'], OBJECTS_INDEX['civil'])
    clauses += generateClausesForObject(status['n'], status['m'], 1, OBJECTS_INDEX['target'])
    clauses += generateClausesForObject(status['n'], status['m'], 1, OBJECTS_INDEX['rope'])
    clauses += generateClausesForObject(status['n'], status['m'], 1, OBJECTS_INDEX['costume'])
    print(len(clauses))

    # case 0,0 est vide
    # on est sûr de ca ?
    clauses.append([(OBJECTS_INDEX['empty'])])

    clauses += addInfoVision(status['n'], status['m'], status['vision'])
    clauses += addInfoListening(status['n'], status['m'], status['position'], status['hear'])

    dimension = status['n'] * status['m'] * len(OBJECTS_INDEX)
    while not isSolutionUnique(clauses, dimension):
        print()
        print("------------------")        


        # action à prendre ici
        c = input("Choix déplacement (0 = move, 1 = clockwise, 2 = anti) : ")
        if c == '0':
            status = referee.move()
        elif c == '1':
            status = referee.turn_clockwise()
        elif c == '2':
            status = referee.turn_anti_clockwise()
        else:
            print("Mauvais choix")
            continue

        pprint({
            "vision": status['vision'],
            "hear": status['hear'],
            "position": status['position'],
            "orientation": status['orientation'],
            "is_in_guard_range": status['is_in_guard_range'],
            "penalties": status['penalties'],
            "status": status['status']
        })
        # input("Press Enter to continue...")
        # attention, addInfoVision que si on n'a pas déjà l'info
        clauses += addInfoVision(status['n'], status['m'], status['vision'])
        print(len(clauses))
        # faire gaffe on doit ajouter plein de fois les memes infos
        # voir comment facilement ne pas les ajouter plusieurs fois
        clauses += addInfoListening(status['n'], status['m'], status['position'], status['hear'])
        print(len(clauses))

    print("Carte connue : \n")
    print(solveur(clauses, dimension))
    map_info = solutionToMap(solveur(clauses, dimension)[1], status['n'], status['m'])
    print("is good solution for referee")
    # ne fonctionne pas pour le moment car on ne met pas les infos des orientations des civils & gardes
    print(referee.send_content(map_info))

if __name__ == "__main__":
    main()