# Sample code from https://www.redblobgames.com/pathfinding/a-star/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

from __future__ import annotations
# some of these types are deprecated: https://www.python.org/dev/peps/pep-0585/
from typing import Protocol, Iterator, Tuple, TypeVar, Optional, List, Dict
T = TypeVar('T')
from pprint import pprint
from aliases import Position, OBJECTS_INDEX, Information

# Location = TypeVar('Location')
Location = str 
class Graph(Protocol):
    def neighbors(self, id: Location) -> list[Location]: 
        return []

class SimpleGraph:
    def __init__(self):
        self.edges: dict[Location, list[Location]] = {}
    
    def neighbors(self, id: Location) -> list[Location]:
        return self.edges[id]

example_graph = SimpleGraph()
example_graph.edges = {
    'A': ['B'],
    'B': ['C'],
    'C': ['B', 'D', 'F'],
    'D': ['C', 'E'],
    'E': ['F'],
    'F': [],
}

import collections

class Queue:
    def __init__(self):
        self.elements = collections.deque()
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, x: T):
        self.elements.append(x)
    
    def get(self) -> T:
        return self.elements.popleft()

# utility functions for dealing with square grids
def from_id_width(id, width):
    return (id % width, id // width)

def draw_tile(graph: SquareGrid, id, style):
    r = " . "
    if 'number' in style and id in style['number']: r = " %-2d" % style['number'][id]
    if 'point_to' in style and (
        style['point_to'].get((id[0], id[1], "N"), None) is not None or 
        style['point_to'].get((id[0], id[1], "S"), None) is not None or 
        style['point_to'].get((id[0], id[1], "E"), None) is not None or 
        style['point_to'].get((id[0], id[1], "W"), None) is not None):
        (x1, y1) = id
        # (x2, y2, direction) = style['point_to'][id]
        x2, y2 = -1, -1
        d = " 1 "
        if style['point_to'].get((id[0], id[1], "N"), None) is not None:
            x2, y2, d = style['point_to'][(id[0], id[1], "N")]
        if style['point_to'].get((id[0], id[1], "S"), None) is not None:
            x2, y2, d = style['point_to'][(id[0], id[1], "S")]
        if style['point_to'].get((id[0], id[1], "E"), None) is not None:
            x2, y2, d = style['point_to'][(id[0], id[1], "E")]
        if style['point_to'].get((id[0], id[1], "W"), None) is not None:
            x2, y2, d = style['point_to'][(id[0], id[1], "W")]
        # print(x1, y1, x2, y2)
        # if x2 == x1 + 1: r = " > "
        # if x2 == x1 - 1: r = " < "
        # if y2 == y1 + 1: r = " v "
        # if y2 == y1 - 1: r = " ^ "
        r = " " + d + " " 
    if 'path' in style and id in style['path']:   r = " @ "
    if 'start' in style and id == style['start']: r = " A "
    if 'goal' in style and id == style['goal']:   r = " Z "
    # if id in graph.walls: r = "###"
    if graph.map[id[1]][id[0]] == OBJECTS_INDEX['wall']: r = "###"
    if graph.map[id[1]][id[0]] in OBJECTS_INDEX['guard']: r = " G "
    return r

def draw_grid(graph, **style):
    print("___" * graph.width)
    for y in range(graph.height):
        for x in range(graph.width):
            print("%s" % draw_tile(graph, (x, y), style), end="")
        print()
    print("~~~" * graph.width)

# data from main article
# DIAGRAM1_WALLS = [from_id_width(id, width=30) for id in [21,22,51,52,81,82,93,94,111,112,123,124,133,134,141,142,153,154,163,164,171,172,173,174,175,183,184,193,194,201,202,203,204,205,213,214,223,224,243,244,253,254,273,274,283,284,303,304,313,314,333,334,343,344,373,374,403,404,433,434]]

GridLocation = Tuple[int, int]
GridLocationDirection = Tuple[int, int, str]

class SquareGrid:
    def __init__(self, width: int, height: int, map):
        self.width = width
        self.height = height
        # self.walls: list[GridLocation] = []
        self.map = map
    
    def in_bounds(self, id: GridLocationDirection) -> bool:
        (x, y, direction) = id
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, id: GridLocationDirection) -> bool:
        (x, y, direction) = id
        # return (x, y) not in self.walls
        newPositionValue = self.map[y][x]
        
        if newPositionValue == OBJECTS_INDEX['wall'] or newPositionValue in OBJECTS_INDEX['guard']:
            return False
        return True
    
    def cost(self, from_node: GridLocationDirection, to_node: GridLocationDirection) -> float:
        return 1
    
    # def neighbors(self, id: GridLocation) -> Iterator[GridLocation]:
    #     (x, y) = id
    #     neighbors = [(x+1, y), (x-1, y), (x, y-1), (x, y+1)] # E W N S
    #     # see "Ugly paths" section for an explanation:
    #     if (x + y) % 2 == 0: neighbors.reverse() # S N W E
    #     results = filter(self.in_bounds, neighbors)
    #     results = filter(self.passable, results)
    #     return results

    def neighbors(self, id: GridLocationDirection) -> Iterator[GridLocationDirection]:
        (x, y, direction) = id
        # to test
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
        
        # neighbors = [(x+1, y), (x-1, y), (x, y-1), (x, y+1)] # E W N S
        # see "Ugly paths" section for an explanation:
        # if (x + y) % 2 == 0: neighbors.reverse() # S N W E
        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return results

class GridWithWeights(SquareGrid):
    def __init__(self, width: int, height: int, map):
        super().__init__(width, height, map)
        # self.weights: dict[GridLocation, float] = {}
    
    def cost(self, from_node: GridLocation, to_node: GridLocation) -> float:
        """
        si un garde nous voit +5
        """
        # TODO
        howManyGuardsAreSeeingUs = 0 # in to_node 
        penalty = howManyGuardsAreSeeingUs * 5
        # return self.weights.get(to_node, 1)
        return 2 - penalty

# diagram4 = GridWithWeights(10, 10)
# diagram4.walls = [(1, 7), (1, 8), (2, 7), (2, 8), (3, 7), (3, 8)]
# diagram4.weights = {loc: 5 for loc in [(3, 4), (3, 5), (4, 1), (4, 2),
#                                        (4, 3), (4, 4), (4, 5), (4, 6),
#                                        (4, 7), (4, 8), (5, 1), (5, 2),
#                                        (5, 3), (5, 4), (5, 5), (5, 6),
#                                        (5, 7), (5, 8), (6, 2), (6, 3),
#                                        (6, 4), (6, 5), (6, 6), (6, 7),
#                                        (7, 3), (7, 4), (7, 5)]}

import heapq

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

def dijkstra_search(graph: GridWithWeights, start: Location, goal: Location):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Location, Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far

# thanks to @m1sp <Jaiden Mispy> for this simpler version of
# reconstruct_path that doesn't have duplicate entries

def reconstruct_path(came_from: dict[Location, Location],
                     start: Location, goal: Location) -> list[Location]:

    current: Location = goal
    path: list[Location] = []
    print("begin reconstruct_path")
    if goal not in came_from: # no path was found
        return []
    while current != start:
        print("current: ", current)
        path.append(current)
        current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    # print('path: ', path)
    return path

import math
def heuristic(a: GridLocation, b: GridLocation) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)
    # manhattan distance
    # return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def heuristic_pts(a: GridLocation) -> float:
    """
    heuristic for points
    compute new cases
    return howManyCasesLeftToSee

    moins il y a de cases à découvrir, plus la valeur est petite

    attention favoriser les cases dans le meme secteur
    ne pas avoir des coins et bordures non vues
    """
    map = [[]]
    return howManyCasesLeftToSee(map)

# def a_star_search(graph: GridWithWeights, start: GridLocationDirection, goal: GridLocation):
#     openList = PriorityQueue()
#     openList.put(start, 0)
#     came_from: dict[GridLocationDirection, Optional[GridLocationDirection]] = {}
#     cost_so_far: dict[GridLocationDirection, float] = {}
#     came_from[start] = None
#     cost_so_far[start] = 0
    
#     while not openList.empty():
#         current: GridLocationDirection = openList.get()
#         # print("current", current)
        
#         if current[0] == goal[0] and current[1] == goal[1]:
#             break
        
#         for next in graph.neighbors(current):
#             # print("next", next)
#             new_cost = cost_so_far[current] + graph.cost(current, next) # every move costs 1 for now
#             if next not in cost_so_far or new_cost < cost_so_far[next]:
#                 # ok on a trouvé une nouvelle route pour aller à next moins chere
#                 cost_so_far[next] = new_cost
#                 priority = new_cost + heuristic((next[0], next[1]), goal)
#                 # priority = new_cost
#                 openList.put(next, priority)
#                 came_from[next] = current
#     return came_from, cost_so_far


def a_star_search(graph: SquareGrid, start: GridLocationDirection, goal: GridLocation):
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

def breadth_first_search(graph: Graph, start: Location, goal: Location):
    frontier = Queue() # queue to store the nodes to be explored
    frontier.put(start)
    came_from: dict[Location, Optional[Location]] = {}
    came_from[start] = None
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            if next not in came_from:
                frontier.put(next)
                came_from[next] = current
    
    return came_from

def howManyCasesLeftToSee(graph: GridWithWeights):
    return 5

def a_star_search_points(graph: GridWithWeights, start: GridLocationDirection):
    '''
    goal: see all the map
    '''
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

        if howManyCasesLeftToSee(graph) == 0:
            break

        for next in graph.neighbors(current):
            # print("next", next)
            new_cost = cost_so_far[current] + graph.cost(current, next) # every move costs 1 for now
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                # ok on a trouvé une nouvelle route pour aller à next moins chere
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic_pts((next[0], next[1]))
                openList.put(next, priority)
                came_from[next] = current
    return came_from, cost_so_far



"""TODO : 
commit
use real map
"""


# map = createMap(10, 10)
# map[5][0] = 1
# diagram_nopath = GridWithWeights(10, 10, map)
# """
# le diagram doit:
# - avoir les murs et les gardes car on ne peut pas passer dessus
# - cost function qui renvoie le cout d'une action (en fonction des regles du jeu, si vu par un garde +5)
# """
# # diagram_nopath.walls = [(5, row) for row in range(10)]
# # weigjts ??= 1
# start: GridLocationDirection = (0, 0, 'N')
# goal: GridLocation = (8, 5)
# came_from, cost_so_far = a_star_search(diagram_nopath, start, goal)
# # came_from, cost_so_far = dijkstra_search(diagram_nopath, start, goal)
# # came_from = breadth_first_search(diagram_nopath, start, goal)
# pprint(came_from)
# print('len came_from', len(came_from))
# # pprint(came_from)
# # pprint(cost_so_far)
# draw_grid(diagram_nopath, point_to=came_from, start=(start[0], start[1]), goal=goal)
# print()
# draw_grid(diagram_nopath, number=cost_so_far, start=(start[0], start[1]), goal=goal)
# new_came_from = {}
# for key, value in came_from.items():
#     if value is not None:
#         if key[0] != value[0] or key[1] != value[1]:
#             new_came_from[(key[0], key[1])] = (value[0], value[1])
#     else: 
#         new_came_from[(key[0], key[1])] = None
# print()
# print(new_came_from)
# draw_grid(diagram_nopath, path=reconstruct_path(new_came_from, start=(start[0], start[1]), goal=goal))

# def createGraph():
    # """hitman graph"""

# diagram = SquareGrid(7, 6, [[1, -1, -1, -1, -1, -1, -1],
#  [1, -1, -1, -1, -1, -1, -1],
#  [9, 6, 8, -1, -1, 3, 5],
#  [-1, -1, -1, 2, -1, -1, -1],
#  [-1, 2, 2, 2, 2, 2, -1],
#  [-1, -1, -1, -1, -1, -1, -1]])
# start: GridLocationDirection = (0, 0, 'N')
# goal: GridLocation = (2, 3)
# came_from, cost_so_far = a_star_search(diagram, start, goal)
# # came_from, cost_so_far = dijkstra_search(diagram_nopath, start, goal)
# # came_from = breadth_first_search(diagram_nopath, start, goal)
# pprint(came_from)
# print('len came_from', len(came_from))
# # pprint(came_from)
# # pprint(cost_so_far)
# draw_grid(diagram, point_to=came_from, start=(start[0], start[1]), goal=goal)
# print()
# draw_grid(diagram, number=cost_so_far, start=(start[0], start[1]), goal=goal)
# new_came_from = {}
# for key, value in came_from.items():
#     if value is not None:
#         if key[0] != value[0] or key[1] != value[1]:
#             new_came_from[(key[0], key[1])] = (value[0], value[1])
#     else: 
#         new_came_from[(key[0], key[1])] = None
# print()
# print(new_came_from)
# draw_grid(diagram, path=reconstruct_path(new_came_from, start=(start[0], start[1]), goal=goal))

