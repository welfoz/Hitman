from typing import List, Tuple
import subprocess
import os
import platform
from enum import Enum

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

# ajout d'une information de vision
def addInfoVision(n_col : int, n_lig : int) -> ClauseBase:
    print("Infos de la case vue : ")
    x = int(input("x : "))
    y = int(input("y : "))
    if x not in range(0,n_col) or y not in range(0,n_lig):
        raise Exception("Coordonnees invalides")
    print("Types possibles : ")
    for key, value in OBJECTS_INDEX.items():
        print(f"'{key}' : {value}")
    typeCase = int(input("Type de la case : "))
    if typeCase not in OBJECTS_INDEX.values():
        raise Exception("Type invalide")
    result = []
    result.append([x * n_lig * 7 + y * 7 + typeCase])
    return result

# ajout d'une information d'écoute
def addInfoListening(n_col : int, n_lig : int) -> ClauseBase:
    print("Position d'Hitman : ")
    x = int(input("x : "))
    y = int(input("y : "))
    if x not in range(0,n_col) or y not in range(0,n_lig):
        raise Exception("Coordonnees invalides")
    print("Nombre de personnes entendues : ")
    n = int(input("n : "))
    if n not in range(0,25):
        raise Exception("Nombre invalide")
    litterals = []
    #pour toutes les cases autour
    for i in range(x-2, x+3):
        for j in range(y-2, y+3):
            if i < 0 or i >= n_col or j < 0 or j >= n_lig:
                continue
            litterals.append(i * n_lig * 7 + j * 7 + OBJECTS_INDEX['guard'])
            litterals.append(i * n_lig * 7 + j * 7 + OBJECTS_INDEX['civil'])
    if n > 5:
        return atLeast(5, litterals)
    return uniqueX(litterals, n)


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

    #print("Solution : \n")
    #print(sol[1])
    sol2 = solveur(clauses + [[-x for x in sol[1]]], dimension)
    if sol2[0]:
        print("Pas d'unicite")
        return False
    else:
        print("Solution unique")
        return True

def atMost(atMostNumber: int, literals: List[Literal], result: List[Literal] = []) -> ClauseBase:
    """
    Generate clauses to express that at most atMostNumber literals in literals are true
    @param atMostNumber: the number of literals that are allowed to be true
    @param literals: the literals that are concerned by the constraint
    @param result: needs to be empty, used for recursion
    """
    if len(result) > atMostNumber:
        return [[-l for l in result]]
    
    clauses = []
    for i in range(len(literals)):
        clauses += atMost(atMostNumber, literals[i+1:], result + [literals[i]])
    return clauses
    
def atLeast(atLeastNumber: int, literals: List[Literal], result: List[Literal] = []) -> ClauseBase:
    """
    Generate clauses to express that at least atLeastNumber literals in literals are true
    @param atLeastNumber: the number of literals that are required to be true
    @param literals: the literals that are concerned by the constraint
    @param result: needs to be empty, used for recursion
    """
    atMostResult = atMost(atLeastNumber - 2, literals, result)

    clauses = []
    for i in range(len(atMostResult)):
        clauses.append(atMostResult[i] + [l for l in literals if -l not in atMostResult[i]])
    return clauses

def uniqueX(literals: List[Literal], x: int) -> ClauseBase:
    """
    Generate clauses to express that exactly x literals in literals are true
    @param literals: the literals that are concerned by the constraint
    @param x: the number of literals that are required to be true
    """

    clauses = []
    
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

def main():

    linesNumber = 3
    columnsNumber = 3
    guardNumber = 1
    civilNumber = 1
    dimension = columnsNumber * linesNumber * len(OBJECTS_INDEX)

    direction = {
        "nord": "n",
        "est": "e",
        "sud": "s",
        "ouest": "o",
        "default": "a" # for any
    }

    map = createMap(columnsNumber, linesNumber)
    # print(map)
    # print(Action.move.value)

    # if we 
    # dont know where a guard looks: ga
    # know where a guard looks: gn, ge, gs, go
    # for civil: ca, cn, ce, cs, co

    clauses = []
    # print(uniqueX([1, 2, 3, 4], 3))
    # clauses += uniqueX([1, 2, 3, 4], 2)
    # clauses += uniqueX([1, 2, 3, 4], 1)
    # print(clauses)

    clauses += generateTypesGrid(columnsNumber, linesNumber)
    clauses += generateClausesForObject(columnsNumber, linesNumber, guardNumber, OBJECTS_INDEX['guard'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, civilNumber, OBJECTS_INDEX['civil'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, 1, OBJECTS_INDEX['target'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, 1, OBJECTS_INDEX['rope'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, 1, OBJECTS_INDEX['costume'])

    while (not isSolutionUnique(clauses, dimension)) and solutionPossible(clauses, dimension)):
        n = input("Nombre de cases vues : ")
        for _ in range(int(n)):
            clauses += addInfoVision(columnsNumber, linesNumber)
        #print(clauses)
        clauses += addInfoListening(columnsNumber, linesNumber)
        probas = probaLitteral(clauses, dimension)
        print("Probas : \n", probas)
        #pour chaque case
        print(probas)
        for i in range(columnsNumber * linesNumber + 1):
            for j in OBJECTS_INDEX.keys():
                print("Case " + str(i) + " avec " + j + " : " + str(probas[i*len(OBJECTS_INDEX) + OBJECTS_INDEX[j] - 1]))
    
    print("Carte connue : \n")
    print(solveur(clauses, dimension))

if __name__ == "__main__":
    main()