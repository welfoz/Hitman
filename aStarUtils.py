# Sample code from https://www.redblobgames.com/pathfinding/a-star/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

from __future__ import annotations
from typing import Iterator, Tuple, List, Optional
from pprint import pprint
from aliases import Position, OBJECTS_INDEX, PositionAction, SPECIAL_ACTIONS, HasObjects, GridLocation
import heapq

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
    def __init__(self, width: int, height: int, map, hasRope: bool = False, hasCostume: bool = False, wearCostume: bool = False, targetKilled: bool = False, ropePosition = None, targetPosition = None):
        self.width = width
        self.height = height
        self.map = map
        self.hasRope = hasRope
        self.hasCostume = hasCostume
        self.wearCostume = wearCostume
        self.targetKilled = targetKilled
        self.ropePosition = ropePosition
        self.targetPosition = targetPosition
    
    def in_bounds(self, id: Position | PositionAction) -> bool:
        x = id[0]
        y = id[1]
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, id: Position | PositionAction) -> bool:
        x = id[0]
        y = id[1]
        newPositionValue = self.map[y][x]
        
        if newPositionValue == OBJECTS_INDEX['wall'] or newPositionValue in OBJECTS_INDEX['guard']:
            return False
        return True
    
    def cost(self, howManyGuardsAreSeeingUs: int, next : Tuple, surroundings : List[Tuple], sat_bonus : float) -> float:
        x, y, d = next
        if (x, y, False) in surroundings:
            return 1 + 5 * howManyGuardsAreSeeingUs + sat_bonus
        return 1 + 5 * howManyGuardsAreSeeingUs
    
    def cost_phase2(self, next, howManyGuardsAreSeeingUs, howManyCivilsAreSeeingUs, wearingCostume, howManyGuardsWillSeeUsWithoutCostume: int) -> float:
        new_cost = 1
        
        if not wearingCostume and howManyGuardsAreSeeingUs > 0:
            # nb de fois vu par un garde * 5
            new_cost += 5 * howManyGuardsAreSeeingUs

        if next[3] == SPECIAL_ACTIONS['neutralize_guard'] or next[3] == SPECIAL_ACTIONS['neutralize_civil']:
            # nb de personnes neutralisées * 20 
            new_cost += 20
            # nb de fois vu en train de neutraliser * 100
            if not wearingCostume:
                new_cost += 100 * (howManyGuardsAreSeeingUs + howManyCivilsAreSeeingUs)
        
        
        if next[3] == SPECIAL_ACTIONS["take_costume"]:
            new_cost -= 5 * howManyGuardsWillSeeUsWithoutCostume
            

        if next[3] == SPECIAL_ACTIONS["put_costume"]:
            # nb de fois vu en train de mettre un costume * 100
            new_cost += 100 * (howManyGuardsAreSeeingUs + howManyCivilsAreSeeingUs)
        
        if next[3] == SPECIAL_ACTIONS["kill_target"]:
            # nb de fois vu en train de tuer la cible * 100
            new_cost += 100 * (howManyGuardsAreSeeingUs + howManyCivilsAreSeeingUs)

        return new_cost
    
    def cost_phase2_without_costume(self, next, howManyGuardsAreSeeingUs, howManyCivilsAreSeeingUs, wearingCostume) -> float:
        new_cost = 1
        
        if not wearingCostume and howManyGuardsAreSeeingUs > 0:
            # nb de fois vu par un garde * 5
            new_cost += 5 * howManyGuardsAreSeeingUs

        if next[3] == SPECIAL_ACTIONS['neutralize_guard'] or next[3] == SPECIAL_ACTIONS['neutralize_civil']:
            # nb de personnes neutralisées * 20 
            new_cost += 20
            # nb de fois vu en train de neutraliser * 100
            if not wearingCostume:
                new_cost += 100 * (howManyGuardsAreSeeingUs + howManyCivilsAreSeeingUs)
        
        if next[3] == SPECIAL_ACTIONS["kill_target"]:
            # nb de fois vu en train de tuer la cible * 100
            new_cost += 100 * (howManyGuardsAreSeeingUs + howManyCivilsAreSeeingUs)

        return new_cost
    
    def neighbors(self, id: Position) -> Iterator[Position]:
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

    def neighbors_phase2(self, id: Position, map, hasObjects: HasObjects, currentGoal: int) -> List[PositionAction]:
        (x, y, direction) = id
        neighbors = []
        firstCase = None
        if direction == 'N':
            # move, turn 90, turn -90
            neighbors = [(x, y+1, 'N', SPECIAL_ACTIONS["nothing_special"], currentGoal),
                         (x, y, 'E', SPECIAL_ACTIONS["nothing_special"], currentGoal),
                         (x, y, 'W', SPECIAL_ACTIONS["nothing_special"], currentGoal)]   
            firstCase = [x, y+1, 'N', OBJECTS_INDEX["empty"]]
        elif direction == 'S':
            neighbors = [(x, y-1, 'S', SPECIAL_ACTIONS["nothing_special"], currentGoal), 
                         (x, y, 'W', SPECIAL_ACTIONS["nothing_special"], currentGoal),
                         (x, y, 'E', SPECIAL_ACTIONS["nothing_special"], currentGoal)]
            firstCase = [x, y-1, "S", OBJECTS_INDEX["empty"]]
        elif direction == 'W':
            neighbors = [(x-1, y, 'W', SPECIAL_ACTIONS["nothing_special"], currentGoal), 
                         (x, y, 'N', SPECIAL_ACTIONS["nothing_special"], currentGoal), 
                         (x, y, 'S', SPECIAL_ACTIONS["nothing_special"], currentGoal)]
            firstCase = [x-1, y, "W", OBJECTS_INDEX["empty"]]
        elif direction == 'E':
            neighbors = [(x+1, y, 'E', SPECIAL_ACTIONS["nothing_special"], currentGoal), 
                         (x, y, 'S', SPECIAL_ACTIONS["nothing_special"], currentGoal), 
                         (x, y, 'N', SPECIAL_ACTIONS["nothing_special"], currentGoal)]
            firstCase = [x+1, y, "E", OBJECTS_INDEX["empty"]]
        else:
            raise ValueError('Invalid direction')
        
        specialActions = []
        if self.in_bounds(firstCase):
            firstCase[3] = map[firstCase[1]][firstCase[0]]

            # we can neutralize if 
            # - we are looking at a guard
            # - the guard isn't looking at us OR we are hidden by a civil
            if firstCase[3] in OBJECTS_INDEX["guard"] \
                and (
                    map[y][x] in OBJECTS_INDEX["civil"] \
                    or (firstCase[3] == OBJECTS_INDEX['guard'][1] and direction != 'S' \
                        or firstCase[3] == OBJECTS_INDEX['guard'][2] and direction != 'N' \
                        or firstCase[3] == OBJECTS_INDEX['guard'][3] and direction != 'W' \
                        or firstCase[3] == OBJECTS_INDEX['guard'][4] and direction != 'E'
                        )
                    ):
                specialActions.append((x, y, direction, SPECIAL_ACTIONS["neutralize_guard"], currentGoal))

                
            if firstCase[3] in OBJECTS_INDEX["civil"] \
                and (
                    map[y][x] in OBJECTS_INDEX["civil"] \
                    or (firstCase[3] == OBJECTS_INDEX['civil'][1] and direction != 'S' \
                        or firstCase[3] == OBJECTS_INDEX['civil'][2] and direction != 'N' \
                        or firstCase[3] == OBJECTS_INDEX['civil'][3] and direction != 'W' \
                        or firstCase[3] == OBJECTS_INDEX['civil'][4] and direction != 'E'
                        )
                    ):
                specialActions.append((x, y, direction, SPECIAL_ACTIONS["neutralize_civil"], currentGoal))

            
        # take costume, need to be on the same case as the costume
        hasCostume = hasObjects.hasCostume
        wearingCostume = hasObjects.wearingCostume
        hasRope = hasObjects.hasRope
        targetKilled = hasObjects.targetKilled
        if not hasCostume and map[y][x] == OBJECTS_INDEX["costume"]:
            specialActions.append((x, y, direction, SPECIAL_ACTIONS["take_costume"], currentGoal))

        # put costume, need to have the costume
        if hasCostume and not wearingCostume: 
            specialActions.append((x, y, direction, SPECIAL_ACTIONS["put_costume"], currentGoal))

        # if dont have the rope and we are on the rope
        if not hasRope and map[y][x] == OBJECTS_INDEX["rope"]:
            specialActions.append((x, y, direction, SPECIAL_ACTIONS["take_rope"], currentGoal + 1))

        # if we have the rope and we are on the target 
        if not targetKilled and hasRope and map[y][x] == OBJECTS_INDEX["target"]:
            specialActions.append((x, y, direction, SPECIAL_ACTIONS["kill_target"], currentGoal + 1))

        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return list(results) + specialActions

    def neighbors_phase2_without_costume(self, id: Position, map, hasObjects: HasObjects, currentGoal: int) -> List[PositionAction]:
        result = self.neighbors_phase2(id, map, hasObjects, currentGoal)
        return list(filter(lambda x: x[3] != SPECIAL_ACTIONS["take_costume"], result))

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