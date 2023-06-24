from typing import List, Tuple, Dict
from enum import Enum

from arbitre_gitlab.hitman.hitman import HC
from collections import namedtuple

# alias de types
Grid = List[List[int]] 
Literal = int
Clause = List[Literal]
ClauseBase = List[Clause]

Orientation = Enum('Orientation', 'N E S W')
Position = Tuple[int, int, Orientation]
PositionAction = Tuple[int, int, Orientation, int, int]
# x, y, value from OBJECTS_INDEX
Information = Tuple[int, int, int]
GridLocation = Tuple[int, int]

OBJECTS_INDEX = {
    'empty': 1,
    'wall': 2,
    'target': 3,
    'rope': 4,
    'costume': 5,
    'guard': [6, 7, 8, 9, 10], # 6 default, 7: north, 8: south, 9: east, 10: west
    'civil': [11, 12, 13, 14, 15] # 11 default, 12: north, 13: south, 14: east, 15: west
}

SPECIAL_ACTIONS = {
    "nothing_special": 0,
    "neutralize_guard": 1,
    "neutralize_civil": 2,
    "take_costume": 3,
    "put_costume": 4,
    "take_rope": 5,
    "kill_target": 6,
}

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



Global_Tuple = namedtuple('Global_Tuple', ['cost_so_far', 'state_map_new_infos', 'backtrack'])
HasObjects = namedtuple('Objects', ['hasRope', 'hasCostume', 'wearingCostume', 'targetKilled'])