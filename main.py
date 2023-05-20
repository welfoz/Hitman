from typing import List, Tuple
import subprocess
import itertools
import os
import platform

# alias de types
Grid = List[List[int]] 
PropositionnalVariable = int
Literal = int
Clause = List[Literal]
ClauseBase = List[Clause]
Model = List[Literal]

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
    objectNumer = len(OBJECTS_INDEX)
    clauses = []
    for i in range(n_col):
        for j in range(n_lig):
            literals = []
            for k in range(objectNumer):
                literals.append(i * n_lig * objectNumer + j * objectNumer + k + 1)
            clauses += uniqueX(literals, 1)
    return clauses

# generation des clauses pour un nombre donne d'ojects dans la carte
def generateClausesForObject(n_col : int, n_lig : int, n_object: int, object_index: int) -> ClauseBase:
    litterals = []
    for i in range(n_col):
        for j in range(n_lig):
            litterals.append(i * n_lig * 7 + j * 7 + object_index)
    r = uniqueX(litterals, n_object)
    print("Clauses pour " + str(n_object) + " " + list(OBJECTS_INDEX.keys())[list(OBJECTS_INDEX.values()).index(object_index)] + " :")
    print(r)
    return r

# ajout d'une information de vision
def addInfoVision(clauses: ClauseBase, n_col : int, n_lig : int) -> ClauseBase:
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
    clauses.append([x * n_lig * 7 + y * 7 + typeCase])
    return clauses

def solveur(clauses: ClauseBase, dimension : int) -> Tuple[bool, List[int]]:
    filename = "temp.cnf"
    dimacs = clausesToDimacs(clauses, dimension)
    write_dimacs_file("\n".join(dimacs), filename)
    return exec_gophersat(filename)

def isSolutionUnique(clauses: ClauseBase, dimension : int) -> bool:
    sol = solveur(clauses, dimension)
    print(sol)
    if not sol[0]: return False

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
    if len(result) > atMostNumber:
        return [[-l for l in result]]
    
    clauses = []
    for i in range(len(literals)):
        clauses += atMost(atMostNumber, literals[i+1:], result + [literals[i]])
    return clauses
    
def atLeast(atLeastNumber: int, literals: List[Literal], result: List[Literal] = []) -> ClauseBase:
    atMostResult = atMost(atLeastNumber - 2, literals, result)

    clauses = []
    for i in range(len(atMostResult)):
        clauses.append(atMostResult[i] + [l for l in literals if -l not in atMostResult[i]])
    return clauses

def uniqueX(literals: List[Literal], x: int) -> ClauseBase:
    clauses = []
    
    for i in range(1, x):
        clauses += atLeast(i, literals)

    clauses += atLeast(x, literals) + atMost(x, literals)
    return clauses

def main():
    linesNumber = 3
    columnsNumber = 3
    guardNumber = 2
    civilNumber = 1
    dimension = columnsNumber * linesNumber * len(OBJECTS_INDEX)

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
    print(clauses)

    while not isSolutionUnique(clauses, dimension):
        addInfoVision(clauses, columnsNumber, linesNumber)
        print(clauses)
    
    print("Carte connue : \n")
    print(solveur(clauses, dimension))


if __name__ == "__main__":
    main()