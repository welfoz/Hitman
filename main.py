from typing import List, Tuple
import subprocess
import itertools
import os

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
    filename: str, cmd: str = os.getcwd() + "\gophersat\gophersat.exe", encoding: str = "utf8"
) -> Tuple[bool, List[int]]:
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

def atLeastOne(literals: List[Literal]) -> ClauseBase:
    return [literals]

def atMostOne(literals: List[Literal]) -> ClauseBase:
    clauses = []
    for i in range(len(literals)):
        for j in range(i + 1, len(literals)):
            clauses.append([-literals[i], -literals[j]])
    return clauses
    
def unique(literals: List[Literal]) -> ClauseBase:
    return atLeastOne(literals) + atMostOne(literals)

# generation des types possibles pour une case
def generateTypesGrid(n_col : int, n_lig : int) -> ClauseBase:
    objectNumer = len(OBJECTS_INDEX)
    clauses = []
    for i in range(n_col):
        for j in range(n_lig):
            literals = []
            for k in range(objectNumer):
                literals.append(i * n_lig * objectNumer + j * objectNumer + k + 1)
            clauses += unique(literals)
    return clauses

# generation des clauses pour un nombre donne d'ojects dans la carte
def generateClausesForObject(n_col : int, n_lig : int, n_object: int, object_index: int) -> ClauseBase:
    clauses = []
    litterals = []
    for i in range(n_col):
        for j in range(n_lig):
            litterals.append(i * n_lig * 7 + j * 7 + object_index)
    for comb in itertools.combinations(litterals, n_object):
        clause = list(comb)
        for l in litterals:
            if l not in clause:
                clause.append(-l)
        clauses.append(clause)
    return clauses

# ajout d'une information de vision
def ajouterInfoVision(clauses: ClauseBase, n_col : int, n_lig : int) -> ClauseBase:
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

def testUnicite(clauses: ClauseBase, dimension : int) -> bool:
    sol = solveur(clauses, dimension)
    #print(sol)
    if not sol[0]: return False

    #print("Solution : \n")
    #print(sol[1])
    sol2 = solveur(clauses + [[-x for x in sol[1]]], dimension)
    if sol2[0]:
        #print("Pas d'unicite")
        return False
    else:
        #print("Solution unique")
        return True

def main():
    linesNumber = 3
    columnsNumber = 3
    guardNumber = 1
    civilNumber = 1
    dimension = columnsNumber * linesNumber * len(OBJECTS_INDEX)

    clauses = []
    clauses += generateTypesGrid(columnsNumber, linesNumber)
    clauses += generateClausesForObject(columnsNumber, linesNumber, guardNumber, OBJECTS_INDEX['guard'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, civilNumber, OBJECTS_INDEX['civil'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, 1, OBJECTS_INDEX['target'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, 1, OBJECTS_INDEX['rope'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, 1, OBJECTS_INDEX['costume'])
    print(clauses)

    while not testUnicite(clauses, dimension):
        ajouterInfoVision(clauses, columnsNumber, linesNumber)
        print(clauses)
    
    print("Carte connue : \n")
    print(solveur(clauses, dimension))


if __name__ == "__main__":
    main()