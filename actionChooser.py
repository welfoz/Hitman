from typing import List, Tuple
import copy

from aliases import Position, OBJECTS_INDEX, PositionAction, SPECIAL_ACTIONS, HasObjects, Global_Tuple
from aStarUtils import SquareGrid, draw_grid, PriorityQueue, GridLocation, Position, Optional
from utils import getAllNewInformation, howManyUnknown, isOutsideTheMap, updateMap
from satUtils import are_surrondings_safe

class ActionChooser:
    def __init__(self, n_col, n_lig):
        self.n_col = n_col 
        self.n_lig = n_lig

    def choose(self, map, position, sat_info : Tuple):
        """
        return the best action to do according to the best path, which maximizes the total information gained
        @param stateTree: list of the values of the total information gained for each path
        """

        diagram = SquareGrid(self.n_col, self.n_lig, map)

        new_goal, howManyUnknown, backtrack = a_star_search_points(diagram, tuple(position), sat_info)
        path = [tuple(position)] + backtrack

        result = fromPathToActionPhase1(path)

        print("Result: " + str(result))
        print('number of actions: ', len(result))
        draw_grid(diagram, start=(position[0], position[1], position[2]), path=path)

        if result[0] == "move":
            return 1
        elif result[0] == "turn 90":
            return 2
        elif result[0] == "turn -90":
            return 3
        else: 
            raise Exception("Error: action not found")

    def choose_phase2(self, map, position: Position, hasRope: bool, hasCostume: bool, wearCostume: bool, targetKilled: bool, ropePosition: Tuple[int, int], targetPosition: Tuple[int, int]):
        """
        return the best action to do according to the best path, which maximizes the total information gained
        @param stateTree: list of the values of the total information gained for each path
        """

        diagram = SquareGrid(self.n_col, self.n_lig, map, hasRope, hasCostume, wearCostume, targetKilled, ropePosition, targetPosition)


        cost_so_far, new_goal, backtrack = a_star_search_points_with_goal(diagram, position)
        path = [tuple(position)] + backtrack
        result = fromPathToActionsPhase2(path)

        pathWithoutActions = []
        for i in range(len(path)):
            pathWithoutActions.append((path[i][0], path[i][1], path[i][2]))

        print("Result: " + str(result))
        print('number of actions: ', len(result))
        draw_grid(diagram, start=(position[0], position[1], position[2]), path=pathWithoutActions)

        actions = []
        for i in range(len(result)):

            if result[i] == "move":
                actions.append(1)
            elif result[i] == "turn 90":
                actions.append(2)
            elif result[i] == "turn -90":
                actions.append(3)
            elif result[i] == "neutralize_guard":
                actions.append(4)
            elif result[i] == "neutralize_civil":
                actions.append(5)
            elif result[i] == "take_rope":
                actions.append(6)
            elif result[i] == "take_costume":
                actions.append(7)
            elif result[i] == "put_costume":
                actions.append(8)
            elif result[i] == "kill_target":
                actions.append(9)
            else: 
                raise Exception("Error: action not found")
        return actions

def getAllPositions(map, object) -> List[Tuple[int, int, int]]:
    positions = []
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] in OBJECTS_INDEX[object]:
                positionValue = map[y][x]
                direction = None

                if positionValue == OBJECTS_INDEX[object][1]:
                    direction = 'N'
                elif positionValue == OBJECTS_INDEX[object][2]:
                    direction = 'S'
                elif positionValue == OBJECTS_INDEX[object][3]:
                    direction = 'E'
                elif positionValue == OBJECTS_INDEX[object][4]:
                    direction = 'W'
                
                positions.append([x, y, direction])
    return positions

def howManyGuardsLookingAtUs(position, map) -> int:
    guardsPositions = getAllPositions(map, "guard")

    guardsLookingAtUs = 0
    for guardPosition in guardsPositions:
        casesSeen = getAllCasesSeenByObject(guardPosition, map, "guard")
        for caseSeen in casesSeen:
            # if we are on the same case as a civil, the guard can't see us
            # if caseSeen is not a civil and we are on it
            if caseSeen[2] not in OBJECTS_INDEX["civil"] and caseSeen[0] == position[0] and caseSeen[1] == position[1]:
                guardsLookingAtUs += 1
        
    return guardsLookingAtUs

def getAllCasesSeenByObject(position, map, object) -> List[Tuple[int, int, int]]:
    vision = None
    if object == "guard":
        vision = 2
    if object == "civil":
        vision = 1

    x = position[0]
    y = position[1]
    direction = position[2]
    computeNewPosition = ["=", "="]
    if direction == 'N':
        computeNewPosition[1] = "+"
    elif direction == 'S':
        computeNewPosition[1] = "-"
    elif direction == 'E':
        computeNewPosition[0] = "+"
    elif direction == 'W':
        computeNewPosition[0] = "-"

    casesSeen = []
    for i in range(vision):
        newPosition = [x, y]
        if computeNewPosition[0] == "+":
            newPosition[0] = x + i + 1
        elif computeNewPosition[0] == "-":
            newPosition[0] = x - i - 1

        if computeNewPosition[1] == "+":
            newPosition[1] = y + i + 1
        elif computeNewPosition[1] == "-":
            newPosition[1] = y - i - 1

        if isOutsideTheMap(len(map[0]), len(map), newPosition): continue
        info = [newPosition[0], newPosition[1], map[newPosition[1]][newPosition[0]]] 

        if info[2] == -1: # unknown cell
            info[2] = OBJECTS_INDEX['empty'] # means we hope to see an empty cell
            casesSeen.append(info)
        elif info[2] == OBJECTS_INDEX['empty']: 
            casesSeen.append(info)
        else: # only see the first objects
            casesSeen.append(info)
            break
    return casesSeen

def howManyCivilsLookingAtUs(position, map) -> int:
    civilsPosition = getAllPositions(map, "civil")

    civilsLookingAtUs = 0
    for civilPosition in civilsPosition:
        casesSeen = getAllCasesSeenByObject(civilPosition, map, "civil")
        for caseSeen in casesSeen:
            # if we are on the same case as a civil, the civil can't see us
            # if caseSeen is not a civil and we are on it
            if caseSeen[2] not in OBJECTS_INDEX["civil"] and caseSeen[0] == position[0] and caseSeen[1] == position[1]:
                civilsLookingAtUs += 1
        # if we are on a civil, he can see us
        if civilPosition[0] == position[0] and civilPosition[1] == position[1]:
            civilsLookingAtUs += 1
        
    return civilsLookingAtUs

def fromPathToActionsPhase2(path):
    """
    input: [(0, 0, 'N'), (0, 0, 'E'), (1, 0, 'E')]
    output: ['move', 'turn 90', 'move']
    """
    if len(path) == 0:
        return []
    actions = []
    for i in range(1, len(path)):
        if path[i][3] == SPECIAL_ACTIONS["nothing_special"]:
            if path[i][0] != path[i - 1][0] or path[i][1] != path[i - 1][1]:
                actions.append('move')
        
            if path[i][2] == 'N':
                if path[i - 1][2] == 'E':
                    actions.append('turn -90')
                elif path[i - 1][2] == 'W':
                    actions.append('turn 90')
            
            if path[i][2] == 'S':
                if path[i - 1][2] == 'E':
                    actions.append('turn 90')
                elif path[i - 1][2] == 'W':
                    actions.append('turn -90')
            
            if path[i][2] == 'E':
                if path[i - 1][2] == 'N':
                    actions.append('turn 90')
                elif path[i - 1][2] == 'S':
                    actions.append('turn -90')
                
            if path[i][2] == 'W':
                if path[i - 1][2] == 'N':
                    actions.append('turn -90')
                elif path[i - 1][2] == 'S':
                    actions.append('turn 90')
        elif path[i][3] == SPECIAL_ACTIONS["neutralize_guard"]:
            actions.append('neutralize_guard')
        elif path[i][3] == SPECIAL_ACTIONS["neutralize_civil"]:
            actions.append('neutralize_civil')
        elif path[i][3] == SPECIAL_ACTIONS["take_costume"]:
            actions.append("take_costume")
        elif path[i][3] == SPECIAL_ACTIONS["put_costume"]:
            actions.append("put_costume")
        elif path[i][3] == SPECIAL_ACTIONS["take_rope"]:
            actions.append("take_rope")
        elif path[i][3] == SPECIAL_ACTIONS["kill_target"]:
            actions.append("kill_target")
        else: 
            raise Exception("Unknown action")
    return actions 

def fromPathToActionPhase1(path):
    """
    input: [(0, 0, 'N'), (0, 0, 'E'), (1, 0, 'E')]
    output: ['move', 'turn 90', 'move']
    """
    if len(path) == 0:
        return []
    actions = []
    for i in range(1, len(path)):
        if path[i][0] != path[i - 1][0] or path[i][1] != path[i - 1][1]:
            actions.append('move')
        
        if path[i][2] == 'N':
            if path[i - 1][2] == 'E':
                actions.append('turn -90')
            elif path[i - 1][2] == 'W':
                actions.append('turn 90')
        
        if path[i][2] == 'S':
            if path[i - 1][2] == 'E':
                actions.append('turn 90')
            elif path[i - 1][2] == 'W':
                actions.append('turn -90')
        
        if path[i][2] == 'E':
            if path[i - 1][2] == 'N':
                actions.append('turn 90')
            elif path[i - 1][2] == 'S':
                actions.append('turn -90')
            
        if path[i][2] == 'W':
            if path[i - 1][2] == 'N':
                actions.append('turn -90')
            elif path[i - 1][2] == 'S':
                actions.append('turn 90')
    return actions 

def getClusteringScore(allUnkownCases):
    """
    return the clustering score of the map
    """
    # compute the distance between each unknown cell

    if len(allUnkownCases) == 0:
        return 0
    if len(allUnkownCases) == 1:
        return 1
    
    distances = []
    for i in range(len(allUnkownCases)):
        for j in range(i + 1, len(allUnkownCases)):
            distance = abs(allUnkownCases[i][0] - allUnkownCases[j][0]) + abs(allUnkownCases[i][1] - allUnkownCases[j][1])
            distances.append(distance)

    return sum(distances)

def a_star_search_points(graph: SquareGrid, start: Position, sat_info : Tuple):
    '''
    but: voir toute la map en un minimum de cost
    '''
    openList = PriorityQueue()
    startTuple = (start, None)
    openList.put(startTuple, 0)
    
    global_dict: dict[Tuple[Position, Optional[Position]], 
        Global_Tuple
    ] = {}
    allUnkownCases = []
    for y in range(len(graph.map)):
        for x in range(len(graph.map[y])):
            if graph.map[y][x] == -1:
                allUnkownCases.append([x, y])

    base_clustering = getClusteringScore(allUnkownCases) 

    minimumValue = base_clustering 

    minimumCostPosition = start
    minimumCostValue = 10000

    global_dict[startTuple] = Global_Tuple(
        cost_so_far=(0, base_clustering),
        state_map_new_infos=[],
        backtrack=[]
    )

    surrondings = are_surrondings_safe(start, sat_info)

    count = 0
    howManyUnknownBase = howManyUnknown(graph.map)
    allInfosBase = [[x, y, graph.map[y][x]] for y in range(len(graph.map)) for x in range(len(graph.map[y])) if graph.map[y][x] != -1]

    while not openList.empty():
        count += 1
        current: Tuple[Position, Optional[Position]] = openList.get()

        current_cost_so_far = global_dict[current].cost_so_far
        current_state_map_new_infos = global_dict[current].state_map_new_infos
        current_backtrack = global_dict[current].backtrack

        if current_backtrack == None:
            global_dict[current] = global_dict[current]._replace(backtrack=[])
        
        
        if current_cost_so_far[1] < minimumValue \
                or (current_cost_so_far[1] == minimumValue and current_cost_so_far[0] < minimumCostValue):
            minimumValue = current_cost_so_far[1]
            minimumCostValue = current_cost_so_far[0]
            minimumCostPosition = current

        allUnkownCases = []
        for y in range(len(graph.map)):
            for x in range(len(graph.map[y])):
                if [x, y, -2] not in current_state_map_new_infos and graph.map[y][x] == -1:
                    allUnkownCases.append([x, y])

        howManyUnknownCurrent = howManyUnknownBase - len(current_state_map_new_infos) 
        if howManyUnknownCurrent == 0:
            # print("goal found")
            break

        for next in graph.neighbors(current[0]):
            nextTuple = (next, current[0])

            caseSeen = getAllNewInformation(graph.width, graph.height, graph.map, next)
            newInfos = [info for info in caseSeen if info not in current_state_map_new_infos and info not in allInfosBase] # we only keep the new information

            howManyGuardsAreSeeingUs = howManyGuardsLookingAtUs(next, graph.map)
            new_cost = current_cost_so_far[0] + graph.cost(howManyGuardsAreSeeingUs, next, surrondings, sat_info[-1]) # default cost = 2, if we know a guard is seeing us, cost = 2 + 5*guards seeing us

            next_state_map_new_infos = [info for info in current_state_map_new_infos] + newInfos
            allUnkownCases = []
            for y in range(len(graph.map)):
                for x in range(len(graph.map[y])):
                    if [x, y, -2] not in next_state_map_new_infos and graph.map[y][x] == -1:
                        allUnkownCases.append([x, y])
            clustering = getClusteringScore(allUnkownCases) 
            if nextTuple not in global_dict or clustering < global_dict[nextTuple].cost_so_far[1] or (clustering == global_dict[nextTuple].cost_so_far[1] and new_cost < global_dict[nextTuple].cost_so_far[0]): # on a trouvé une nouvelle route pour aller à nextTuple moins chere
                # si on trouve une route apportant plus d'information pour aller à nextTuple, on la prend
                next_backtrack = current_backtrack + [nextTuple[0]]

                next_cost_so_far = (new_cost, clustering)



                # closiestUnknownDistance = 1000
                # for unknown in allUnkownCases:
                #     distance = manhattan_distance(unknown, (next[0], next[1]))
                #     if distance < closiestUnknownDistance:
                #         closiestUnknownDistance = distance
                # # print(closiestUnknownDistance)
                # if len(allUnkownCases) == 0:
                #     closiestUnknownDistance = 0
                
                # if closiestUnknownDistance > 2:
                #     closiestUnknownDistance -= 2

                # but de l'heuristique: estimer le mieux la penalité restante jusqu'à ne plus avoir de case inconnue
                # priority = new_cost + fartherUnknownDistance + getClusteringScore(allUnkownCases)
                priority = new_cost + getClusteringScore(allUnkownCases) / 2 #+ closiestUnknownDistance
                # priority = howManyUnknown(nextMap) # pretty efficient but not best result
                # priority = new_cost + score # inneficient but find the best result as it expends more than others
                # priority = new_cost + score * 10 # get stuck, why ? circular path
                # priority = new_cost # diskstra
                
                openList.put(nextTuple, priority)

                global_dict[nextTuple] = Global_Tuple(
                    cost_so_far=next_cost_so_far,
                    state_map_new_infos=next_state_map_new_infos,
                    backtrack=next_backtrack
                )
            
    # print("total count: ", count)
    # print('len nodes: ', len(list(global_dict.keys())))

    return minimumCostPosition, minimumValue, global_dict[minimumCostPosition].backtrack

def manhattan_distance(a: GridLocation, b: GridLocation) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2) 

def a_star_search_points_with_goal(graph: SquareGrid, start: Position):
    """basic a star search
    to go from start to goal

    goal 1: take rope
    goal 2: kill target
    goal 3: go to goal
    """
    ropePosition = graph.ropePosition
    targetPosition = graph.targetPosition
    targetKilled = graph.targetKilled
    startPosition = start

    openList = PriorityQueue()
    startTuple = ((start[0], start[1], start[2], SPECIAL_ACTIONS['nothing_special'], 1), None)
    openList.put(startTuple, 0)

    cost_so_far: dict[Tuple[PositionAction, Optional[PositionAction]], float] = {}
    hasObjects: dict[Tuple[PositionAction, Optional[PositionAction]], HasObjects] = {}

    cost_so_far[startTuple] = 0
    hasObjects[startTuple] = HasObjects(
        hasCostume=graph.hasCostume, 
        wearingCostume=graph.wearCostume, 
        hasRope=graph.hasRope, 
        targetKilled=graph.targetKilled
    )

    state_map: dict[Tuple[PositionAction, Optional[PositionAction]], List[List[int]]] = {}
    state_map[startTuple] = graph.map

    backtrack = {}
    backtrack[startTuple] = []
    howManyGuardsWillSeeUsWithoutCostume, _ = a_star_search_points_without_costume(graph, start, (startPosition[0], startPosition[1]), 1)
    
    while not openList.empty():
        currentTuple: Tuple[PositionAction, Optional[PositionAction]]  = openList.get()
        current = currentTuple[0]

        if backtrack.get(currentTuple, None) == None:
            backtrack[currentTuple] = []
        
        current_x, current_y, current_direction, current_action, current_goal = current
        if current_x == startPosition[0] and current_y == startPosition[1] and current_goal == 3:
            break
        
        for next in graph.neighbors_phase2((current_x, current_y, current_direction), state_map[currentTuple], hasObjects[currentTuple], current_goal):
            nextTuple = (next, current)
            nextMap = state_map[currentTuple]
            x_next, y_next, direction_next, action_next, goal_next = next

            howManyGuardsAreSeeingUs = howManyGuardsLookingAtUs(next, nextMap)
            howManyCivilsAreSeeingUs = howManyCivilsLookingAtUs(next, nextMap)

            new_cost = cost_so_far[currentTuple] + graph.cost_phase2(
                next=next, 
                wearingCostume=hasObjects[currentTuple].wearingCostume, 
                howManyCivilsAreSeeingUs=howManyCivilsAreSeeingUs,
                howManyGuardsAreSeeingUs=howManyGuardsAreSeeingUs,
                howManyGuardsWillSeeUsWithoutCostume=howManyGuardsWillSeeUsWithoutCostume
            ) 
            
            if nextTuple not in cost_so_far or new_cost < cost_so_far[nextTuple]:
                # on a trouvé une nouvelle route pour aller à next moins chere
                backtrack[nextTuple] = backtrack[currentTuple] + [nextTuple[0]]

                hasObjects[nextTuple] = hasObjects[currentTuple]

                if action_next == SPECIAL_ACTIONS['neutralize_guard'] or action_next == SPECIAL_ACTIONS['neutralize_civil']:
                    if direction_next == "N":
                        nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next, y_next + 1, OBJECTS_INDEX["empty"]]])
                    elif direction_next == "S":
                        nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next, y_next - 1, OBJECTS_INDEX["empty"]]])
                    elif direction_next == "E":
                        nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next + 1, y_next, OBJECTS_INDEX["empty"]]])
                    elif direction_next == "W":
                        nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next - 1, y_next, OBJECTS_INDEX["empty"]]])
                elif action_next == SPECIAL_ACTIONS["take_costume"]:
                    hasObjects[nextTuple] = hasObjects[nextTuple]._replace(hasCostume=True)
                    nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next, y_next, OBJECTS_INDEX["empty"]]])
                elif action_next == SPECIAL_ACTIONS["put_costume"]:
                    hasObjects[nextTuple] = hasObjects[nextTuple]._replace(wearingCostume=True)
                    # hasObjects[nextTuple] = (hasObjects[currentTuple][0], True, hasObjects[currentTuple][2], hasObjects[currentTuple][3])
                elif action_next == SPECIAL_ACTIONS["take_rope"]:
                    hasObjects[nextTuple] = hasObjects[nextTuple]._replace(hasRope=True)
                    nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next, y_next, OBJECTS_INDEX["empty"]]])
                elif action_next == SPECIAL_ACTIONS["kill_target"]:
                    hasObjects[nextTuple] = hasObjects[nextTuple]._replace(targetKilled=True)
                    nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next, y_next, OBJECTS_INDEX["empty"]]])                

                cost_so_far[nextTuple] = new_cost
                state_map[nextTuple] = nextMap
                heuristic = None
                if not hasObjects[nextTuple].hasRope and goal_next == 1:
                    # goal 1: take costume
                    heuristic = manhattan_distance((next[0], next[1]), (ropePosition[0], ropePosition[1]))
                elif not hasObjects[nextTuple].targetKilled and goal_next == 2:
                    # goal 2: kill target
                    heuristic = manhattan_distance((next[0], next[1]), (targetPosition[0], targetPosition[1]))
                elif hasObjects[nextTuple].targetKilled and goal_next == 3:
                    # goal 3: go to goal = start
                    heuristic = manhattan_distance((next[0], next[1]), (startPosition[0], startPosition[1]))
                else: 
                    raise Exception("should not happen")


                priority = new_cost + heuristic # manhattan distance

                openList.put(nextTuple, priority)
    print("Coût prevu: ", cost_so_far[currentTuple])
    return cost_so_far, currentTuple, backtrack[currentTuple]

def a_star_search_points_without_costume(graph: SquareGrid, start: Position, goal: Tuple[int, int], startGoal: int):
    """basic a star search
    to go from start to goal

    goal 1: take rope
    goal 2: kill target
    goal 3: go to goal
    """
    ropePosition = graph.ropePosition
    targetPosition = graph.targetPosition
    targetKilled = graph.targetKilled
    startPosition = start

    openList = PriorityQueue()
    startTuple = ((start[0], start[1], start[2], SPECIAL_ACTIONS['nothing_special'], startGoal), None)
    openList.put(startTuple, 0)

    # cost, howManyGuardsAreSeeingUs
    cost_so_far: dict[Tuple[PositionAction, Optional[PositionAction]], Tuple[float, int]] = {}
    # Tuple[bool, bool] = (hasCostume, wearingCostume, hasRope, targetKilled)
    hasObjects: dict[Tuple[PositionAction, Optional[PositionAction]], HasObjects] = {}

    cost_so_far[startTuple] = (0, 0)
    hasObjects[startTuple] = HasObjects(
        hasCostume=graph.hasCostume, 
        wearingCostume=graph.wearCostume, 
        hasRope=graph.hasRope, 
        targetKilled=graph.targetKilled
    )

    state_map: dict[Tuple[PositionAction, Optional[PositionAction]], List[List[int]]] = {}
    state_map[startTuple] = graph.map

    backtrack = {}
    backtrack[startTuple] = []
    
    while not openList.empty():
        currentTuple: Tuple[PositionAction, Optional[PositionAction]]  = openList.get()
        current = currentTuple[0]

        if backtrack.get(currentTuple, None) == None:
            backtrack[currentTuple] = []
        
        current_x, current_y, current_direction, current_action, current_goal = current
        if current_x == goal[0] and current_y == goal[1] and current_goal == 3:
            break
        
        for next in graph.neighbors_phase2_without_costume((current_x, current_y, current_direction), state_map[currentTuple], hasObjects[currentTuple], current_goal):
            nextTuple = (next, current)
            nextMap = state_map[currentTuple]
            # need to build the map according to graph.map and all infos
            x_next, y_next, direction_next, action_next, goal_next = next

            howManyGuardsAreSeeingUs = howManyGuardsLookingAtUs(next, nextMap)
            howManyCivilsAreSeeingUs = howManyCivilsLookingAtUs(next, nextMap)

            new_cost = cost_so_far[currentTuple][0] + graph.cost_phase2_without_costume(
                next=next, 
                wearingCostume=hasObjects[currentTuple][1], 
                howManyCivilsAreSeeingUs=howManyCivilsAreSeeingUs,
                howManyGuardsAreSeeingUs=howManyGuardsAreSeeingUs
            ) 
            
            if nextTuple not in cost_so_far or new_cost < cost_so_far[nextTuple][0]:
                # ok on a trouvé une nouvelle route pour aller à next moins chere
                backtrack[nextTuple] = backtrack[currentTuple] + [nextTuple[0]]

                hasObjects[nextTuple] = hasObjects[currentTuple]

                if action_next == SPECIAL_ACTIONS['neutralize_guard'] or action_next == SPECIAL_ACTIONS['neutralize_civil']:
                    if direction_next == "N":
                        nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next, y_next + 1, OBJECTS_INDEX["empty"]]])
                    elif direction_next == "S":
                        nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next, y_next - 1, OBJECTS_INDEX["empty"]]])
                    elif direction_next == "E":
                        nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next + 1, y_next, OBJECTS_INDEX["empty"]]])
                    elif direction_next == "W":
                        nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next - 1, y_next, OBJECTS_INDEX["empty"]]])
                elif action_next == SPECIAL_ACTIONS["take_rope"]:
                    hasObjects[nextTuple] = hasObjects[nextTuple]._replace(hasRope=True)
                    nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next, y_next, OBJECTS_INDEX["empty"]]])
                elif action_next == SPECIAL_ACTIONS["kill_target"]:
                    hasObjects[nextTuple] = hasObjects[nextTuple]._replace(targetKilled=True)
                    nextMap = updateMap(copy.deepcopy(state_map[currentTuple]), [[x_next, y_next, OBJECTS_INDEX["empty"]]])                

                cost_so_far[nextTuple] = (new_cost, cost_so_far[currentTuple][1] + howManyGuardsAreSeeingUs)
                state_map[nextTuple] = nextMap
                heuristic = None
                if not hasObjects[nextTuple].hasRope and goal_next == 1:
                    # goal 1: take costume
                    heuristic = manhattan_distance((next[0], next[1]), (ropePosition[0], ropePosition[1]))
                elif not hasObjects[nextTuple].targetKilled and goal_next == 2:
                    # goal 2: kill target
                    heuristic = manhattan_distance((next[0], next[1]), (targetPosition[0], targetPosition[1]))
                elif hasObjects[nextTuple].targetKilled and goal_next == 3:
                    # goal 3: go to goal = start
                    heuristic = manhattan_distance((next[0], next[1]), (startPosition[0], startPosition[1]))
                else: 
                    raise Exception("should not happen")


                priority = new_cost + heuristic # manhattan distance

                openList.put(nextTuple, priority)
    print("cost prevu: ", cost_so_far[currentTuple])
    return cost_so_far[currentTuple][1], backtrack[currentTuple]
