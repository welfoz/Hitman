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
                if map[j][i] in range(HCInfoToObjectIndexFull(HC.GUARD_N.value), HCInfoToObjectIndexFull(HC.GUARD_S.value) + 1):
                    guardsOrCivils -= 1
                if map[j][i] in range(HCInfoToObjectIndexFull(HC.CIVIL_N.value), HCInfoToObjectIndexFull(HC.CIVIL_S.value) + 1):
                    guardsOrCivils -= 1
                # print("Case deja connue", i, j, map[j][i], guardsOrCivils)
                continue
            
            for g in range(OBJECTS_INDEX['guard'][0], OBJECTS_INDEX['guard'][4]):
                litterals.append(i * n_lig * 7 + j * 7 + g)
            for c in range(OBJECTS_INDEX['civil'][0], OBJECTS_INDEX['civil'][4]):
                litterals.append(i * n_lig * 7 + j * 7 + c)
    
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
        litterals.append(i * n_lig * 7 + y * 7 + OBJECTS_INDEX['guard'][3])
    for i in range(x+1, x+3):
        if i < 0 or i >= n_col:
            continue
        litterals.append(i * n_lig * 7 + y * 7 + OBJECTS_INDEX['guard'][4])
    # cases verticales
    for j in range(y-2, y):
        if j < 0 or j >= n_lig:
            continue
        litterals.append(x * n_lig * 7 + j * 7 + OBJECTS_INDEX['guard'][1])
    for j in range(y+1, y+3):
        if j < 0 or j >= n_lig:
            continue
        litterals.append(x * n_lig * 7 + j * 7 + OBJECTS_INDEX['guard'][2])
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

## savoir si un garde peut nous voir sur une case
def is_position_safe(position : Tuple, clauses : ClauseBase, n_col : int, n_lig : int, dimension : int) -> bool:
    clauses += addInfoIsInGuardRange(n_col, n_lig, position)
    sol = solveur(clauses, dimension)
    return not sol[0]