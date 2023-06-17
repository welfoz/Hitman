from typing import List, Tuple, Dict
from pprint import pprint
from itertools import combinations

from aliases import  Literal, ClauseBase, Orientation, Information, Position
from arbitre_gitlab.hitman.hitman import HC, HitmanReferee
from utils import getKeyFromValue, OBJECTS_INDEX, HCInfoToObjectIndexFull

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

def ObjectIndexToMapGuardIndex(value : int) -> int:
    if value == OBJECTS_INDEX['empty']:
        return MAP_GUARD_INDEX['empty']
    if value == OBJECTS_INDEX['wall']:
        return MAP_GUARD_INDEX['blocking']
    if value == OBJECTS_INDEX['target']:
        return MAP_GUARD_INDEX['blocking']
    if value == OBJECTS_INDEX['rope']:
        return MAP_GUARD_INDEX['blocking']
    if value == OBJECTS_INDEX['costume']:
        return MAP_GUARD_INDEX['blocking']
    if value in OBJECTS_INDEX['guard']:
        return MAP_GUARD_INDEX['guard']
    if value in OBJECTS_INDEX['civil']:
        return MAP_GUARD_INDEX['civil']

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
    result.append([(OBJECTS_INDEX['empty'])])
    return result

def addInfoVision(n_col : int, n_lig : int, info_vision : Information) -> ClauseBase:
    # print("Info vision : " + str(info_vision))
    x = info_vision[0]
    y = info_vision[1]
    value = ObjectIndexToMapGuardIndex(info_vision[2])
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
                continue
            
            litterals.append(i * n_lig * 4 + j * 4 + MAP_GUARD_INDEX['guard'])
            litterals.append(i * n_lig * 4 + j * 4 + MAP_GUARD_INDEX['civil'])
    
    if len(litterals) > 0:
        if nb_heard > 4:
            return atLeast(guardsOrCivils, litterals)
        return uniqueX(litterals, guardsOrCivils)
    return []

# prise en compte du is_in_guard_range
def addInfoIsInGuardRange(n_col : int, n_lig : int, position : Tuple, seen : int) -> ClauseBase:
    x = position[0]
    y = position[1]
    litterals = []
    # cases horizontales
    for i in range(x-2, x):
        if i < 0 or i >= n_col:
            continue
        litterals.append(i * n_lig * 4 + y * 4 + MAP_GUARD_INDEX['guard'])
    for i in range(x+1, x+3):
        if i < 0 or i >= n_col:
            continue
        litterals.append(i * n_lig * 4 + y * 4 + MAP_GUARD_INDEX['guard'])
    # cases verticales
    for j in range(y-2, y):
        if j < 0 or j >= n_lig:
            continue
        litterals.append(x * n_lig * 4 + j * 4 + MAP_GUARD_INDEX['guard'])
    for j in range(y+1, y+3):
        if j < 0 or j >= n_lig:
            continue
        litterals.append(x * n_lig * 4 + j * 4 + MAP_GUARD_INDEX['guard'])
    # print(litterals)
    if seen == 1:
        return atLeast(1, litterals)
    else:
        return []

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
    # optimisation : pour enlever les doublons, passer en set de tuples puis retourner en liste de listes
    set_clause = set([tuple(c) for c in clauses])
    clean_clauses = list(set_clause)
    for clause in clean_clauses:
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
        return MAP_GUARD_INDEX['guard']
    if value in range(HC.CIVIL_N._value_, HC.CIVIL_W._value_ + 1):
        return MAP_GUARD_INDEX['civil']
    if value == HC.EMPTY._value_:
        return MAP_GUARD_INDEX['empty']
    
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
            cases.append((i, j, HCInfoToGuardIndex(map[j][i])))
        result.append(cases)
    return result

def is_position_safe(position : Tuple, known_map : dict[Tuple[int, int], HC], clauses : ClauseBase, n_col : int, n_lig : int) -> bool:
    dimension = n_col * n_lig * 4
    if HCInfoToGuardIndex(known_map[position[1]][position[0]]) == GUARD_INDEX['blocking']:
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
                clauses += [[s[1][0] * n_lig * 4 + s[1][1] * 4 + GUARD_INDEX['guard']]]
                sol = solveur(clauses, dimension)
                clauses.remove([s[1][0] * n_lig * 4 + s[1][1] * 4 + GUARD_INDEX['guard']])
                if sol[0]:
                    return False
        if s[0][2] == GUARD_INDEX['unknown']:
            clauses += [[s[0][0] * n_lig * 4 + s[0][1] * 4 + GUARD_INDEX['guard']]]
            sol = solveur(clauses, dimension)
            clauses.remove([s[0][0] * n_lig * 4 + s[0][1] * 4 + GUARD_INDEX['guard']])
            if sol[0]:
                return False
            if s[1][2] == GUARD_INDEX['unknown']:
                clauses += [[s[1][0] * n_lig * 4 + s[1][1] * 4 + GUARD_INDEX['guard']]]
                sol = solveur(clauses, dimension)
                clauses.remove([s[1][0] * n_lig * 4 + s[1][1] * 4 + GUARD_INDEX['guard']])
                if sol[0]:
                    return False
    return True

def extract_sub_map(map : List[List[int]], position : Tuple) -> Tuple:
    x = position[0]
    y = position[1]
    sub_map = []
    for i in range(y - 2, y + 3):
        if 0 <= i < len(map):
            if x-2 > 0:
                ligne = map[i][x - 2:x + 3]
            else:
                ligne = map[i][0:x + 3]
            sub_map.append(ligne)
    if x-2 > 0:
        sub_position_x = 2
    else:
        sub_position_x = x
    if y-2 > 0:
        sub_position_y = 2
    else:
        sub_position_y = y
    for x in range(len(sub_map)):
        for y in range(len(sub_map[0])):
            sub_map[x][y] = HCInfoToGuardIndex(sub_map[x][y])
    return sub_map, (sub_position_x, sub_position_y)

def addInfoMap(n_col : int, n_lig : int, sub_map : List[List[int]]) -> ClauseBase:
    clauses = []
    for x in range(n_col):
        for y in range(n_lig):
            if sub_map[y][x] != -1:
                clauses += [[x * n_lig * 4 + y * 4 + sub_map[y][x]]]
    return clauses

def is_position_safe_opti(position : Tuple, map : List[List[int]], heard_map : List[List[int]], seen_map : List[List[int]], n_col : int, n_lig : int) -> bool:
    sub_map, sub_position = extract_sub_map(map, position)
    n_col_sub_map = len(sub_map[0])
    n_lig_sub_map = len(sub_map)
    clauses = generateTypesGrid(n_col_sub_map, n_lig_sub_map)
    clauses += addInfoListening(n_col_sub_map, n_lig_sub_map, sub_position, heard_map[sub_position[1]][sub_position[0]], sub_map)
    for x in range(n_col_sub_map):
        for y in range(n_lig_sub_map):
            if heard_map[y][x] == 0:
                clauses += addInfoListening(n_col_sub_map, n_lig_sub_map, (x, y), heard_map[y][x], sub_map)
    clauses += addInfoMap(n_col_sub_map, n_lig_sub_map, sub_map)
    for x in range(n_col_sub_map):
        for y in range(n_lig_sub_map):
            clauses += addInfoIsInGuardRange(n_col_sub_map, n_lig_sub_map, (x,y), seen_map[y][x])
    # print("Clauses : ", len(clauses))
    return is_position_safe(sub_position, sub_map, clauses, n_col_sub_map, n_lig_sub_map)