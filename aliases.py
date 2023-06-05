from typing import List, Tuple, Dict
from enum import Enum

from arbitre_gitlab.hitman.hitman import HC

# alias de types
Grid = List[List[int]] 
Literal = int
Clause = List[Literal]
ClauseBase = List[Clause]

# Orientation = Enum(HC.N, HC.E, HC.S, HC.W)
Orientation = Enum('Orientation', 'N E S W')
Position = Tuple[int, int, Orientation]
# x, y, value from OBJECTS_INDEX
Information = Tuple[int, int, int]

OBJECTS_INDEX = {
    'empty': 1,
    'wall': 2,
    'target': 3,
    'rope': 4,
    'costume': 5,
    'guard': [6, 8, 9, 10, 11], # 6 default, 7: north, 8: south, 9: east, 10: west
    'civil': [7, 12, 13, 14, 15], # 11 default, 12: north, 13: south, 14: east, 15: west
}

"""
[1, 1, 1, 5, 6, -1, -1]
[1, 2, X, 1, 1, 1, 1]
[3, 2, 1, 1, 1, 7, -1]
[2, 2, 1, 6, -1, -1, -1]
[1, 1, 1, 1, 1, 1, -1]
[1, 1, 2, -1, -1, -1, -1]
"""


"""
[1, 1, 1, 5, 6, -1, -1]
[-1, 2, 1, 1, 1, 1, 1]
[-1, 2, 1, 1, 1, 7, X]
[2, 2, 1, 6, -1, -1, -1]
[1, 1, 1, 1, 1, 1, -1]
[1, 1, 2, -1, -1, -1, -1]
"""
"""
[-1, -1, 1, -1, -1, -1, -1]
[-1, -1, 1, -1, -1, -1, -1]
[-1, -1, 1, -1, -1, -1, -1]
[2, 2, 1, 6, -1, -1, -1]
[1, 1, 1, 1, 1, 1, -1]
[1, 1, 2, -1, -1, -1, -1]
"""

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

def main():
    print(count_dupplicate_clauses())
    print('ok')

# main()
