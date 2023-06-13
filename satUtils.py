from typing import List, Tuple, Dict
from pprint import pprint
from itertools import combinations

from aliases import  Literal, ClauseBase, Orientation, Information, Position, OBJECTS_INDEX
from arbitre_gitlab.hitman.hitman import HC, HitmanReferee
from utils import getKeyFromValue, HCInfoToObjectIndexFull

import subprocess
import os
import platform
import time


GUARD_INDEX = {
    'unknown' : -1,
    'empty': 1,
    'blocking': 2,
    'guard': 3,
}

MAP_GUARD_INDEX = {
    'empty': 1,
    'blocking': 2,
    'guard': 3,
    'civil': 4
}

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

# generation des types possibles pour une case
def generateTypesGrid(n_col : int, n_lig : int) -> ClauseBase:
    objectNumber = len(MAP_GUARD_INDEX)
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
            litterals.append(i * n_lig * 4 + j * 4 + object_index)
    r = uniqueX(litterals, n_object)
    #print("Clauses pour " + str(n_object) + " " + list(OBJECTS_INDEX.keys())[list(OBJECTS_INDEX.values()).index(object_index)] + " :")
    #print(r)
    return r

def generateInitialClauses(n_col : int, n_lig : int, n_guards : int, n_civils : int) -> ClauseBase:
    result = []
    result += generateTypesGrid(n_col, n_lig)
    result += generateClausesForObject(n_col, n_lig, n_guards, MAP_GUARD_INDEX['guard'])
    result += generateClausesForObject(n_col, n_lig, n_civils, MAP_GUARD_INDEX['civil'])
    return result

def addInfoVision(n_col : int, n_lig : int, info_vision : Information) -> ClauseBase:
    print("Info vision : " + str(info_vision))
    x = info_vision[0]
    y = info_vision[1]
    value = HCInfoToMapGuardIndex(info_vision[2])
    # print("Clauses pour les infos de vision : ")
    # print(result)
    return [[x * n_lig * 4 + y * 4 + value]]

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
                if map[j][i] in range(HCInfoToObjectIndexFull(HC.GUARD_N.value), HCInfoToObjectIndexFull(HC.GUARD_S.value) + 1):
                    guardsOrCivils -= 1
                if map[j][i] in range(HCInfoToObjectIndexFull(HC.CIVIL_N.value), HCInfoToObjectIndexFull(HC.CIVIL_S.value) + 1):
                    guardsOrCivils -= 1
                # print("Case deja connue", i, j, map[j][i], guardsOrCivils)
                continue
            
            litterals.append(i * n_lig * 4 + j * 4 + MAP_GUARD_INDEX['guard'])
            litterals.append(i * n_lig * 4 + j * 4 + MAP_GUARD_INDEX['civil'])
    
    if len(litterals) > 0:
        if nb_heard > 4:
            return atLeast(guardsOrCivils, litterals)
        return uniqueX(litterals, guardsOrCivils)
    return []

# prise en compte du is_in_guard_range
def addInfoIsInGuardRange(n_col : int, n_lig : int, position : Tuple) -> ClauseBase:
    x = position[0]
    y = position[1]
    litterals = []
    # cases horizontales
    for i in range(x-2, x):
        if i < 0 or i >= n_col:
            continue
        litterals.append(i * n_lig * 3 + y * 3 + OBJECTS_INDEX['guard'])
    for i in range(x+1, x+3):
        if i < 0 or i >= n_col:
            continue
        litterals.append(i * n_lig * 3 + y * 3 + GUARD_INDEX['guard'])
    # cases verticales
    for j in range(y-2, y):
        if j < 0 or j >= n_lig:
            continue
        litterals.append(x * n_lig * 3 + j * 3 + GUARD_INDEX['guard'])
    for j in range(y+1, y+3):
        if j < 0 or j >= n_lig:
            continue
        litterals.append(x * n_lig * 3 + j * 3 + GUARD_INDEX['guard'])
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

# calcule la proba de chaque littéral dans les solutions du solveur
# def probaLitteral(clauses: ClauseBase, dimension : int) -> List[float]:
#     proba = [0] * dimension
#     n = 0
#     sol = solveur(clauses, dimension)
#     while sol[0] & (n < 1001):
#         n += 1
#         for c in sol[1]:
#             if c > 0:
#                 proba[c-1] += 1
#             else:
#                 proba[-c-1] -= 1
#         sol = solveur(clauses + [[-x for x in sol[1]]], dimension)
#     return [p/(n) for p in proba]

# def solutionToMap(solution: List[int], n_col : int, n_lig : int) -> Dict[Tuple[int, int], HC]:
#     objectNumber = len(OBJECTS_INDEX)
#     map_info: Dict[Tuple[int, int], HC] = {}
#     map_info_readable: Dict[Tuple[int, int], HC] = {}

#     for i in range(n_col):
#         for j in range(n_lig):
#             for k in range(objectNumber):
#                 if solution[i * n_lig * objectNumber + j * objectNumber + k] > 0:
#                     map_info_readable[(i, j)] = getKeyFromValue(OBJECTS_INDEX, k + 1)
#                     ## need to keep the map with guard N ...
#                     map_info[(i, j)] = k + 1
#     pprint(map_info_readable)
#     return map_info

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

## open the temp.cnf file and count the number of dupplicate clauses
def count_dupplicate_clauses() -> int:
    with open('temp.cnf', 'r') as f:
        lines = f.readlines()
        clauses = []
        # print(lines)
        for line in lines:
            if line[0] != 'c':
                clauses.append(line)
        
        clausesset = list(set(clauses))
        return len(lines), len(clauses), len(clausesset), len(clauses) - len(clausesset), (len(clauses) - len(clausesset)) / len(clauses)

def HCInfoToGuardIndex(value : int) -> int:
    if value == HC.WALL._value_ or value in range(HC.CIVIL_N._value_, HC.PIANO_WIRE._value_ + 1):
        return GUARD_INDEX['blocking']
    if value in range(HC.GUARD_N._value_, HC.GUARD_W._value_ + 1):
        return GUARD_INDEX['guard']
    if value == HC.EMPTY._value_:
        return GUARD_INDEX['empty']
    else:
        return GUARD_INDEX['unknown']
    
def HCInfoToMapGuardIndex(value : int) -> int:
    if value == HC.WALL._value_ or value in range(HC.TARGET._value_, HC.PIANO_WIRE._value_ + 1):
        return MAP_GUARD_INDEX['blocking']
    if value in range(HC.GUARD_N._value_, HC.GUARD_W._value_ + 1):
        return GUARD_INDEX['guard']
    if value in range(HC.CIVIL_N._value_, HC.CIVIL_W._value_ + 1):
        return GUARD_INDEX['civil']
    if value == HC.EMPTY._value_:
        return GUARD_INDEX['empty']
    
# renvoie les 4 paires de 2 cases autour de la position
def get_surroundings(position, map, n_col, n_lig) -> List[Information]:
    x = position[0]
    y = position[1]
    result = []
    surroundings = [[(x-1, y), (x-2, y)], [(x+1, y), (x+2, y)], [(x, y-1), (x, y-2)], [(x, y+1), (x, y+2)]]
    for d in surroundings: # for each direction
        cases = []
        for c in d: # for each case
            i = c[0]
            j = c[1]
            if i < 0 or i >= n_col or j < 0 or j >= n_lig:
                cases.append((i, j, GUARD_INDEX['blocking']))
                continue
            cases.append((i, j, HCInfoToGuardIndex(map[(i, j)].value)))
        result.append(cases)
    return result

def is_position_safe(position : Tuple, known_map : dict[Tuple[int, int], HC], clauses : ClauseBase, n_col : int, n_lig : int, dimension : int) -> bool:
    if HCInfoToGuardIndex(known_map[(position[0], position[1])].value) == GUARD_INDEX['blocking']:
        return True
    surroundings = get_surroundings(position, known_map, n_col, n_lig)
    for s in surroundings:
        # pour chaque direction
        if s[0][2] == GUARD_INDEX['guard']:
            return False
        if s[1][2] == GUARD_INDEX['guard']:
            return False
        if s[0][2] == GUARD_INDEX['blocking']:
            # elle cache la 2eme
            continue
        if s[0][2] == GUARD_INDEX['empty']:
            if s[1][2] == GUARD_INDEX['guard']:
                return False
            if s[1][2] == GUARD_INDEX['blocking'] or s[1] == GUARD_INDEX['empty']:
                continue
            if s[1][2] == GUARD_INDEX['unknown']:
                clauses += [[s[1][0] * n_lig * 15 + s[1][1] * 15 + GUARD_INDEX['guard'][0]]] #  a maj !!!
                sol = solveur(clauses, dimension)
                if sol[0]:
                    return False
        if s[0][2] == GUARD_INDEX['unknown']:
            clauses += [[s[0][0] * n_lig * 15 + s[0][1] * 15 + GUARD_INDEX['guard'][0]]] #  a maj !!!
            sol = solveur(clauses, dimension)
            if sol[0]:
                return False
            if s[1][2] == GUARD_INDEX['unknown']:
                clauses += [[s[1][0] * n_lig * 15 + s[1][1] * 15 + GUARD_INDEX['guard'][0]]]
                sol = solveur(clauses, dimension)
                if sol[0]:
                    return False
    return True