from typing import List, Tuple
import subprocess
import itertools

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

def exec_gophersat(
    filename: str, cmd: str = "gophersat", encoding: str = "utf8"
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
    dimacs = "p cnf " + str(pow(dimension, 3)) + ' ' + str(len(clauses))

    result = []
    for clause in clauses:
        line = ""
        for literal in clause:
            line += str(literal) + " "
        line += "0"
        result.append(line)

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

def main():
    linesNumber = 2
    columnsNumber = 2
    guardNumber = 1
    civilNumber = 1

    clauses = []
    clauses += generateTypesGrid(columnsNumber, linesNumber)
    clauses += generateClausesForObject(columnsNumber, linesNumber, guardNumber, OBJECTS_INDEX['guard'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, civilNumber, OBJECTS_INDEX['civil'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, 1, OBJECTS_INDEX['target'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, 1, OBJECTS_INDEX['rope'])
    clauses += generateClausesForObject(columnsNumber, linesNumber, 1, OBJECTS_INDEX['costume'])
    print(clauses)

if __name__ == "__main__":
    main()