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

# def gridtoClause(grid: Grid) -> ClauseBase: 
#     clauses = []

#     for i in range(len(grid)):
#         for j in range(len(grid[i])):
#             if grid[i][j] != 0:
#                 clauses.append([i*(pow(len(grid), 2)) + j*(len(grid)) + grid[i][j]])

#     return clauses

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
    
# def uniqueLinesAndColumns(grid: Grid) -> ClauseBase:
#     clauses = []
#     dimension = len(grid)
#     # lines 
#     for i in range(dimension):
#         for j in range(dimension):
#             literals = []
#             for k in range(dimension):
#                 literals.append(i*(pow(dimension, 2)) + j*(dimension) + k + 1)
#             clauses += unique(literals)
#             print(unique(literals))
#             print("-----------")
    
#     # columns 
#     for i in range(dimension):
#         for j in range(dimension):
#             literals = []
#             for k in range(dimension):
#                 literals.append(i*(pow(dimension, 2)) + j*(dimension) + k + 1)
#             clauses += unique(literals) 
#     return clauses

# generation des types possibles pour une case
def generateTypesGrid(n_col : int, n_lig : int, nLitterauxUtilises : int) -> Tuple[ClauseBase, int]:
    clauses = []
    for i in range(n_col):
        for j in range(n_lig):
            literals = []
            for k in range(7):
                literals.append(nLitterauxUtilises + i * n_lig * 7 + j * 7 + k + 1)
            clauses += unique(literals)
    return clauses, nLitterauxUtilises + len(clauses)

# generation du nombre de gardes sur la carte
# part du principe que generateTypesGrid a ete appele en tout premier (et que le litteral pour le garde en 11 est 3)
def generateNumGuards(n_col : int, n_lig : int, n_gar : int, nLitterauxUtilises : int) -> Tuple[ClauseBase, int]:
    clauses = []
    litterals = []
    for i in range(n_col):
        for j in range(n_lig):
            litterals.append(i * n_lig * 7 + j * 7 + 3)
    for comb in itertools.combinations(litterals, n_gar):
        clause = list(comb)
        for l in litterals:
            if l not in clause:
                clause.append(-l)
        clauses.append(clause)
    return clauses, nLitterauxUtilises + len(clauses)

# generation du nombre de gardes sur la carte
# part du principe que generateTypesGrid a ete appele en tout premier (et que le litteral pour le civil en 11 est 4)
def generateNumCivils(n_col : int, n_lig : int, n_civ : int, nLitterauxUtilises : int) -> Tuple[ClauseBase, int]:
    clauses = []
    litterals = []
    for i in range(n_col):
        for j in range(n_lig):
            litterals.append(i * n_lig * 7 + j * 7 + 4)
    for comb in itertools.combinations(litterals, n_civ):
        clause = list(comb)
        for l in litterals:
            if l not in clause:
                clause.append(-l)
        clauses.append(clause)
    return clauses, nLitterauxUtilises + len(clauses)

def main():
    # print(generateNumCivils(3, 3, 2, 28)[0])


if __name__ == "__main__":
    main()