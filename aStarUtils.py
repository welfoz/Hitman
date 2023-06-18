# Sample code from https://www.redblobgames.com/pathfinding/a-star/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

from __future__ import annotations
from typing import Iterator, Tuple, TypeVar, Optional, List, Dict
T = TypeVar('T')
from pprint import pprint
from aliases import Position, OBJECTS_INDEX, Information
import heapq
from satUtils import is_position_safe_opti

GridLocation = Tuple[int, int]
GridLocationDirection = Tuple[int, int, str]

def draw_tile(graph: SquareGrid, id, style):
    r = " . "
    if 'number' in style and id in style['number']: r = " %-2d" % style['number'][id]
    if 'point_to' in style and (
        style['point_to'].get((id[0], id[1], "N"), None) is not None or 
        style['point_to'].get((id[0], id[1], "S"), None) is not None or 
        style['point_to'].get((id[0], id[1], "E"), None) is not None or 
        style['point_to'].get((id[0], id[1], "W"), None) is not None):
        d = " 1 "
        if style['point_to'].get((id[0], id[1], "N"), None) is not None:
            x2, y2, d = style['point_to'][(id[0], id[1], "N")]
        if style['point_to'].get((id[0], id[1], "S"), None) is not None:
            x2, y2, d = style['point_to'][(id[0], id[1], "S")]
        if style['point_to'].get((id[0], id[1], "E"), None) is not None:
            x2, y2, d = style['point_to'][(id[0], id[1], "E")]
        if style['point_to'].get((id[0], id[1], "W"), None) is not None:
            x2, y2, d = style['point_to'][(id[0], id[1], "W")]
        r = " " + d + " " 
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['wall']: r = "###"
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['target']: r = " T "
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['guard'][1]: r = "GNG"
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['guard'][2]: r = "GSG"
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['guard'][3]: r = "GEG"
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['guard'][4]: r = "GWG"
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['rope']: r = " R "
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['costume']: r = " C "
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['civil'][1]: r = "CNC"
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['civil'][2]: r = "CSC"
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['civil'][3]: r = "CEC"
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['civil'][4]: r = "CWC"

    if graph.map[id[1]][id[0]] == -1 : r = " ? "

    # get last direction on this case
    indexes = {
        "N": -1,
        "S": -1,
        "E": -1,
        "W": -1,
    }
    found = False
    if 'path' in style and (id[0], id[1], "N") in style['path']:   
        indexes["N"] = style['path'].index((id[0], id[1], "N"))
        found = True
    if 'path' in style and (id[0], id[1], "S") in style['path']:   
        indexes["S"] = style['path'].index((id[0], id[1], "S"))
        found = True
    if 'path' in style and (id[0], id[1], "E") in style['path']:   
        indexes["E"] = style['path'].index((id[0], id[1], "E"))
        found = True
    if 'path' in style and (id[0], id[1], "W") in style['path']:   
        indexes["W"] = style['path'].index((id[0], id[1], "W"))
        found = True
    if found == True:
        values = list(indexes.values())
        indexOfMax = values.index(max(values))
        keys = list(indexes.keys())
        direction = keys[indexOfMax]
        r = " " + direction + " "

    if 'start' in style and (id[0], id[1], "N") == style['start']:   
        r = "ANA"
    if 'start' in style and (id[0], id[1], "S") == style['start']:   
        r = "ASA"
    if 'start' in style and (id[0], id[1], "E") == style['start']:   
        r = "AEA"
    if 'start' in style and (id[0], id[1], "W") == style['start']:   
        r = "AWA"

    if 'goal' in style and id == style['goal']:   r = " Z "
    return r

def draw_grid(graph, **style):
    pprint("___" * graph.width)
    map = []
    for y in range(graph.height):
        line = []
        for x in range(graph.width):
            line.append("%s" % draw_tile(graph, (x, y), style))
        map.append(line)
    
    map.reverse()
    for line in map:
        print("".join(line))
    print("~~~" * graph.width)

class SquareGrid:
    def __init__(self, width: int, height: int, map):
        self.width = width
        self.height = height
        self.map = map
    
    def in_bounds(self, id: GridLocationDirection) -> bool:
        (x, y, direction) = id
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, id: GridLocationDirection) -> bool:
        (x, y, direction) = id
        newPositionValue = self.map[y][x]
        
        if newPositionValue == OBJECTS_INDEX['wall'] or newPositionValue in OBJECTS_INDEX['guard']:
            return False
        return True
    
    def cost(self, howManyGuardsAreSeeingUs: int, sat_info : Tuple, next : Tuple, count : int) -> float:
        if (count == 1):
            sat_map, sat_heard_map, sat_seen_map, n_col, n_lig, sat_bonus = sat_info
            if not is_position_safe_opti(next, sat_map, sat_heard_map, sat_seen_map, n_col, n_lig):
                return 1 + 5 * howManyGuardsAreSeeingUs + sat_bonus
        # each action costs 1
        return 1 + 5 * howManyGuardsAreSeeingUs
    
    def neighbors(self, id: GridLocationDirection) -> Iterator[GridLocationDirection]:
        (x, y, direction) = id
        neighbors = []
        if direction == 'N':
            # move, turn 90, turn -90
            neighbors = [(x, y+1, 'N'), (x, y, 'E'), (x, y, 'W')]
        elif direction == 'S':
            neighbors = [(x, y-1, 'S'), (x, y, 'W'), (x, y, 'E')]
        elif direction == 'W':
            neighbors = [(x-1, y, 'W'), (x, y, 'N'), (x, y, 'S')]
        elif direction == 'E':
            neighbors = [(x+1, y, 'E'), (x, y, 'S'), (x, y, 'N')]
        else:
            raise ValueError('Invalid direction')
        
        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return results

class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, T]] = [] # type: ignore
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self) -> T:
        """
        Returns the item with the lowest priority
        """
        return heapq.heappop(self.elements)[1]

def heuristic(a: GridLocation, b: GridLocation) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(graph: SquareGrid, start: GridLocationDirection, goal: GridLocation):
    """basic a star search
    to go from start to goal
    """
    openList = PriorityQueue()
    openList.put(start, 0)
    came_from: dict[GridLocationDirection, Optional[GridLocationDirection]] = {}
    cost_so_far: dict[GridLocationDirection, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not openList.empty():
        current: GridLocationDirection = openList.get()
        # print("current", current)
        
        if current[0] == goal[0] and current[1] == goal[1]:
            break
        
        for next in graph.neighbors(current):
            # print("next", next)
            new_cost = cost_so_far[current] + graph.cost(current, next) # every move costs 1 for now
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                # ok on a trouvé une nouvelle route pour aller à next moins chere
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic((next[0], next[1]), goal)
                # priority = new_cost
                openList.put(next, priority)
                came_from[next] = current
    return came_from, cost_so_far
