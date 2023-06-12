
from typing import List, Tuple, Dict
import subprocess
import os
import platform
from aliases import OBJECTS_INDEX, Information
from aliases import  ClauseBase, Orientation, Information, Position, OBJECTS_INDEX

from arbitre_gitlab.hitman.hitman import HC

def updateMap(map, newInfo: Information):
    """
    update the map with the new information
    @param map: the map of the game
    @param newInfo: the new information to update the map
    """
    for info in newInfo:
        map[info[1]][info[0]] = info[2]
    return map

def createMap(n_col, n_lig):
    """
    Create a map of size n_col * n_lig
    @param n_col: number of columns
    @param n_lig: number of lines
    """
    map = []
    for i in range(n_lig):
        map.append([])
        for _ in range(n_col):
            map[i].append(-1)
    print(map)
    return map

def isInformationAlreadyKnown(map, information: Information) -> bool:
    """
    return true if the information is already known
    @param map: the map of the game
    @param information: the information to check [x, y, value]
    """
    if map[information[1]][information[0]] == information[2]:
        return True
    return False

def isOutsideTheMap(n_col, n_lig, coordinates: Tuple[int, int]) -> bool:
    """
    return true if the coordinates are outside the map
    @param coordinates: the coordinates of the cell [x, y]
    """
    if coordinates[0] < 0 or coordinates[1] < 0:
        return True
    if coordinates[0] >= n_col or coordinates[1] >= n_lig:
        return True
    return False

def getAllNewInformation(n_col, n_lig, map, position) -> List[Tuple[int, int, int]]:
    """
    return all new information the position reveals compared to the map
    @param map: the map of the game
    @param position: the position of the agent [x, y, direction]
    """
    vision = 3
    x = position[0]
    y = position[1]
    direction = position[2]
    computeNewPosition = ["=", "="]
    if direction == 'N':
        computeNewPosition[1] = "+"
    elif direction == 'S':
        computeNewPosition[1] = "-"
    elif direction == 'E':
        computeNewPosition[0] = "+"
    elif direction == 'W':
        computeNewPosition[0] = "-"

    casesSeen = []
    for i in range(vision):
        newPosition = [x, y]
        if computeNewPosition[0] == "+":
            newPosition[0] = x + i + 1
        elif computeNewPosition[0] == "-":
            newPosition[0] = x - i - 1

        if computeNewPosition[1] == "+":
            newPosition[1] = y + i + 1
        elif computeNewPosition[1] == "-":
            newPosition[1] = y - i - 1

        if isOutsideTheMap(n_col, n_lig, newPosition): continue

        info = [newPosition[0], newPosition[1], map[newPosition[1]][newPosition[0]]] 

        if info[2] == -1: # unknown cell
            info[2] = OBJECTS_INDEX['empty'] # means we hope to see an empty cell
            casesSeen.append(info)
        elif info[2] != OBJECTS_INDEX['empty']: # can't see through objects
            break

    return casesSeen

def howManyUnknown(map: List[List[int]]) -> int:
    unknown = 0
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] == -1:
                unknown += 1
    return unknown

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

def isMapComplete(map: List[List[HC]]) -> bool:
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] == -1:
                return False
    return True

## open the temp.cnf file and count the number of dupplicate clauses
def count_dupplicate_clauses() -> int:
    with open('./Hitman/temp.cnf', 'r') as f:
        lines = f.readlines()
        clauses = []
        # print(lines)
        for line in lines:
            if line[0] != 'c':
                clauses.append(line)
        
        clausesset = list(set(clauses))
        return len(lines), len(clauses), len(clausesset), len(clauses) - len(clausesset), (len(clauses) - len(clausesset)) / len(clauses)
