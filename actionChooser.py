from typing import List, Tuple
import copy
from pprint import pprint

from aliases import Position, OBJECTS_INDEX, Information
from aStarUtils import SquareGrid, draw_grid, PriorityQueue, GridLocation, GridLocationDirection, Optional
from utils import createMap, getAllNewInformation, howManyUnknown, isInformationAlreadyKnown, isOutsideTheMap, updateMap

# class ActionChoice:
#     def __init__(self, n_col, n_lig):
#         self.n_col = n_col 
#         self.n_lig = n_lig
#         self.depth_max = 6

#     def isLookingAtABorder(self, position) -> bool:
#         """
#         return true if the agent is looking at a border
#         @param map: the map of the game
#         @param parentPosition: the position of the agent [x, y, direction]
#         """
#         direction = position[2]
#         if direction == 'N':
#             if position[1] == self.n_lig - 1:
#                 return True 
#         elif direction == 'S':
#             if position[1] == 0:
#                 return True 
#         elif direction == 'E':
#             if position[0] == self.n_col - 1:
#                 return True 
#         elif direction == 'W':
#             if position[0] == 0:
#                 return True 
#         return False

#     def isLookingAtAnImpassableObstacle(self, position, map) -> bool:
#         x = position[0]
#         y = position[1]
#         direction = position[2]
#         newPositionValue = None

#         if direction == 'N':
#             newPositionValue = map[y + 1][x]
#         elif direction == 'S':
#             newPositionValue = map[y - 1][x]
#         elif direction == 'E':
#             newPositionValue = map[y][x + 1]
#         elif direction == 'W':
#             newPositionValue = map[y][x - 1]

#         if newPositionValue == OBJECTS_INDEX['wall'] or newPositionValue in OBJECTS_INDEX['guard']:
#             return True
#         return False

#     def computePositionBasedOnAction(self, position: Position, action, map)-> Position:
#         direction = position[2]
#         coordinates = [position[0], position[1]]
#         newDirection = direction

#         if action == 1:
#             # move
#             if self.isLookingAtABorder(position) or self.isLookingAtAnImpassableObstacle(position, map):
#                 pass
#             elif direction == 'N':
#                 coordinates[1] += 1
#             elif direction == 'S':
#                 coordinates[1] -= 1
#             elif direction == 'E':
#                 coordinates[0] += 1
#             elif direction == 'W':
#                 coordinates[0] -= 1
#         elif action == 2:
#             # turn 90
#             if direction == 'N':
#                 newDirection = 'E'
#             elif direction == 'S':
#                 newDirection = 'W'
#             elif direction == 'E':
#                 newDirection = 'S'
#             elif direction == 'W':
#                 newDirection = 'N'
#         elif action == 3:
#             # turn -90
#             if direction == 'N':
#                 newDirection = 'W'
#             elif direction == 'S':
#                 newDirection = 'E'
#             elif direction == 'E':
#                 newDirection = 'N'
#             elif direction == 'W':
#                 newDirection = 'S'

#         return coordinates + [newDirection]

#     # position changes according to the action
#     def createStateTree(self, map, position: Position):
#         """
#         computes the total information gained for each path with DEPTH_MAX depth
#         return a list of the values of the total information gained for each path 
#         @param map: the map of the game
#         @param position: the position of the agent [x, y, direction]
#         """
#         stateTree = [0]
#         positionTree = [position]
#         stateMap = [map]
#         depthCount = 1
#         for _ in range(self.depth_max):
#             for _ in range(pow(3, depthCount)):
#                 parentIndex = (len(stateTree) - 1) // 3
#                 parentPosition = positionTree[parentIndex]
#                 parentMap = stateMap[parentIndex]

#                 # action is 1, 2 or 3
#                 action = ((len(stateTree) - 1) % 3) + 1

#                 newPosition = self.computePositionBasedOnAction(parentPosition, action, parentMap)

#                 newInfo = getAllNewInformation(self.n_col, self.n_lig, parentMap, newPosition)
#                 # print("newPosition: " + str(newPosition))
#                 # print("newInfo: " + str(newInfo))
#                 newMap = updateMap(copy.deepcopy(parentMap), newInfo)
#                 # print("newMap: " + str(newMap))

#                 if newPosition == parentPosition:
#                     totalInformationGained = -10000
#                 else:
#                     totalInformationGained = stateTree[parentIndex] + self.informationGained(newPosition, newInfo, map)

#                 # améliorable en stockant que la derniere position
#                 stateTree.append(totalInformationGained)
#                 # améliorable en stockant que la derniere position
#                 positionTree.append(newPosition)
#                 # améliorable en stockant que la derniere position
#                 stateMap.append(newMap)

#                 # print("----")
#                 # print("parentIndex: " + str(parentIndex))
#                 # print("index: " + str(len(stateTree) - 1))
#                 # print("action: " + str(action))
#                 # print("newPosition: " + str(newPosition))
#                 # print("information: " + str(newInfo))
#                 # print("totalInformationGained: " + str(totalInformationGained))
#             depthCount += 1
#         return stateTree

#     def choose(self, map, position):
#         """
#         return the best action to do according to the best path, which maximizes the total information gained
#         @param stateTree: list of the values of the total information gained for each path
#         """
#         farthestCases = self.farthestCasesWithNewInformation(position, map, 50)
#         nearestCases = farthestCases
#         print(nearestCases)
#         bestResult = []
#         howManyUnknownBefore = howManyUnknown(map)
#         bestHowManyUnknown = 100000
#         bestScore = 0
#         bestPath = None
#         diagram = SquareGrid(self.n_col, self.n_lig, map)
#         for case in nearestCases:
#             path, howManyUnknownVariable, clusteringScore = astar(self.n_col, self.n_lig, map, position, case, diagram)
#             result = fromPathToActions(path)

#             # on favorise les chemins courts
#             score = (howManyUnknownBefore - howManyUnknownVariable) / len(result)

#             # if howManyUnknownVariable < bestHowManyUnknown: # favorise la découverte
#             if score > bestScore:
#                 bestScore = score
#                 bestResult = result
#                 bestHowManyUnknown = howManyUnknownVariable
#                 bestPath = path
#             print("----")
#             print("case: " + str(case))
#             print("result: " + str(result))
#             print("howManyUnknownVariable: " + str(howManyUnknownVariable))
#             print("score: " + str(score))
#             print("clusteringScore: " + str(clusteringScore))

#         print("bestResult: " + str(bestResult))
#         print("bestHowManyUnknown: " + str(bestHowManyUnknown))
#         draw_grid(diagram, start=(position[0], position[1], position[2]), path=bestPath)
#         if bestResult[0] == "move":
#             return 1
#         elif bestResult[0] == "turn 90":
#             return 2
#         elif bestResult[0] == "turn -90":
#             return 3
#         else: 
#             raise Exception("Error: action not found")

#     def getAllCasesSeenByGuard(self, position, map) -> List[Tuple[int, int, int]]:
#         vision = 2
#         x = position[0]
#         y = position[1]
#         direction = position[2]
#         computeNewPosition = ["=", "="]
#         if direction == 'N':
#             computeNewPosition[1] = "-"
#         elif direction == 'S':
#             computeNewPosition[1] = "+"
#         elif direction == 'E':
#             computeNewPosition[0] = "+"
#         elif direction == 'W':
#             computeNewPosition[0] = "-"

#         casesSeen = []
#         for i in range(vision):
#             newPosition = [x, y]
#             if computeNewPosition[0] == "+":
#                 newPosition[0] = x + i + 1
#             elif computeNewPosition[0] == "-":
#                 newPosition[0] = x - i - 1

#             if computeNewPosition[1] == "+":
#                 newPosition[1] = y + i + 1
#             elif computeNewPosition[1] == "-":
#                 newPosition[1] = y - i - 1

#             if isOutsideTheMap(self.n_col, self.n_lig, newPosition): continue
#             info = [newPosition[0], newPosition[1], map[newPosition[1]][newPosition[0]]] 

#             casesSeen.append(info)

#             # if case not empty, vision stops here
#             if info[2] != OBJECTS_INDEX['empty']: 
#                 break
#         return casesSeen

#     def getAllGuardsPositions(self, map) -> List[Tuple[int, int, int]]:
#         guardsPositions = []
#         for y in range(len(map)):
#             for x in range(len(map[y])):
#                 if map[y][x] in OBJECTS_INDEX['guard']:
#                     guardPositionValue = map[y][x]
#                     direction = None

#                     # can change with the arbitre
#                     if guardPositionValue == OBJECTS_INDEX['guard'][1]:
#                         direction = 'N'
#                     elif guardPositionValue == OBJECTS_INDEX['guard'][2]:
#                         direction = 'S'
#                     elif guardPositionValue == OBJECTS_INDEX['guard'][3]:
#                         direction = 'E'
#                     elif guardPositionValue == OBJECTS_INDEX['guard'][4]:
#                         direction = 'W'
                    
#                     guardsPositions.append([x, y, direction])
#         return guardsPositions

#     def howManyGuardsLookingAtUs(self, position, map) -> int:
#         guardsPositions = self.getAllGuardsPositions(map)

#         guardsLookingAtUs = 0
#         for guardPosition in guardsPositions:
#             casesSeen = self.getAllCasesSeenByGuard(guardPosition, map)
#             for caseSeen in casesSeen:
#                 if caseSeen[0] == position[0] and caseSeen[1] == position[1]:
#                     guardsLookingAtUs += 1
            
#         return guardsLookingAtUs

#     def informationGained(self, position, newInfo, map) -> int:
#         """
#         return the information gained by doing action to the parent value
#         """
#         newCases = len(newInfo)
#         # penalty = self.howManyGuardsLookingAtUs(position, map) * 5

#         # for now we don't take into account the penalty
#         # return newCases * 2 - penalty
#         return newCases

#     def nearestCasesWithNewInformation(self, position, map, numberOfCasesWanted: int) -> List[Tuple[int, int]]:
#         """
#         return the nearest case with new information
#         @param map: the map of the game
#         @param position: the position of the agent [x, y, direction]
#         """
#         # new information is the case with value -1
#         allUnkownCases = []
#         for y in range(len(map)):
#             for x in range(len(map[y])):
#                 if map[y][x] == -1:
#                     allUnkownCases.append([x, y])
        
#         nearestCases = []
#         while len(nearestCases) < numberOfCasesWanted and len(allUnkownCases) > 0:
#             nearestDistance = 1000000
#             nearestCase = None
#             for case in allUnkownCases:
#                 distance = self.distanceBetweenTwoCases(position, case)
#                 if distance < nearestDistance:
#                     nearestCase = case
#                     nearestDistance = distance
#             if nearestCase == None:
#                 raise Exception("No nearest case found")
#             nearestCases.append(nearestCase)
#             allUnkownCases.remove(nearestCase)

#         return nearestCases

class ActionChooser:
    def __init__(self, n_col, n_lig):
        self.n_col = n_col 
        self.n_lig = n_lig

    def choose(self, map, position):
        """
        return the best action to do according to the best path, which maximizes the total information gained
        @param stateTree: list of the values of the total information gained for each path
        """
        farthestCases = self.farthestCasesWithNewInformation(position, map, 50)
        nearestCases = farthestCases
        print(nearestCases)
        bestResult = []
        howManyUnknownBefore = howManyUnknown(map)
        bestHowManyUnknown = 100000
        bestScore = 0
        bestPath = None
        diagram = SquareGrid(self.n_col, self.n_lig, map)
        for case in nearestCases:
            path, howManyUnknownVariable, clusteringScore = astar(self.n_col, self.n_lig, map, position, case, diagram)
            result = fromPathToActions(path)

            # on favorise les chemins courts
            score = (howManyUnknownBefore - howManyUnknownVariable) / len(result)

            # if howManyUnknownVariable < bestHowManyUnknown: # favorise la découverte
            if score > bestScore:
                bestScore = score
                bestResult = result
                bestHowManyUnknown = howManyUnknownVariable
                bestPath = path
            print("----")
            print("case: " + str(case))
            print("result: " + str(result))
            print("howManyUnknownVariable: " + str(howManyUnknownVariable))
            print("score: " + str(score))
            print("clusteringScore: " + str(clusteringScore))

        print("bestResult: " + str(bestResult))
        print("bestHowManyUnknown: " + str(bestHowManyUnknown))
        draw_grid(diagram, start=(position[0], position[1], position[2]), path=bestPath)
        if bestResult[0] == "move":
            return 1
        elif bestResult[0] == "turn 90":
            return 2
        elif bestResult[0] == "turn -90":
            return 3
        else: 
            raise Exception("Error: action not found")

    def farthestCasesWithNewInformation(self, position, map, numberOfCasesWanted: int) -> List[Tuple[int, int]]:
        """
        return the farthest case with new information
        @param map: the map of the game
        @param position: the position of the agent [x, y, direction]
        """
        # new information is the case with value -1
        allUnkownCases = []
        for y in range(len(map)):
            for x in range(len(map[y])):
                if map[y][x] == -1:
                    allUnkownCases.append([x, y])
        
        farthestCases = []
        while len(farthestCases) < numberOfCasesWanted and len(allUnkownCases) > 0:
            farthestDistance = 0
            farthestCase = None
            for case in allUnkownCases:
                distance = self.distanceBetweenTwoCases(position, case)
                if distance > farthestDistance:
                    farthestCase = case
                    farthestDistance = distance
            if farthestCase == None:
                raise Exception("No nearest case found")
            farthestCases.append(farthestCase)
            allUnkownCases.remove(farthestCase)

        return farthestCases
    
    def distanceBetweenTwoCases(self, case1, case2) -> int:
        """
        return the distance between two cases
        @param case1: the first case [x, y]
        @param case2: the second case [x, y]
        """
        return abs(case1[0] - case2[0]) + abs(case1[1] - case2[1])

def astar(n_col, n_lig, map, start, goal, diagram):
    came_from, cost_so_far, new_goal, howManyUnknown, clusteringScore = a_star_search_points(diagram, tuple(start), tuple(goal))

    if howManyUnknown == None:
        raise Exception("No new goal found")

    if new_goal != None:
        goal = new_goal
        # print("new_goal", new_goal)
    else: 
        raise Exception("No new goal found")
    # print("came_from", came_from)

    new_came_from = {}
    for key, value in came_from.items():
        if value is not None:
            if key[0] != value[0] or key[1] != value[1]:
                new_came_from[(key[0], key[1])] = (value[0], value[1])
        else: 
            new_came_from[(key[0], key[1])] = None
    new_cost = {}
    for key, value in cost_so_far.items():
        if value is not None:
            new_cost[(key[0], key[1])] = value
            # if key[0] != value[0] or key[1] != value[1]:
            #     new_cost[(key[0], key[1])] = (value[0], value[1])
        else: 
            new_cost[(key[0], key[1])] = None
    path = reconstruct_path_real(came_from, start=tuple(start), goal=tuple(goal))
    
    # draw_grid(diagram, number=new_cost, start=(start[0], start[1]), goal=goal)
    # draw_grid(diagram, start=(start[0], start[1], start[2]), path=path)
    return path, howManyUnknown, clusteringScore

def reconstruct_path_real(came_from: dict[str, str],
                    start: str, goal: Tuple[int, int, str]) -> list[str]:

    current = goal

    path: list[str] = []

    goalFound = False
    for key, value in came_from.items():
        if key[0] == goal[0] and key[1] == goal[1]:
            goalFound = True
            break
    if not goalFound:
        return []

    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    return path

def fromPathToActions(path):
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

def getClusteringScore(map):
    """
    return the clustering score of the map
    """
    # compute the distance between each unknown cell
    allUnkownCases = []
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] == -1:
                allUnkownCases.append([x, y])
    
    if len(allUnkownCases) == 0 or len(allUnkownCases) == 1:
        return 0
    
    distances = []
    for i in range(len(allUnkownCases)):
        for j in range(i + 1, len(allUnkownCases)):
            distances.append(abs(allUnkownCases[i][0] - allUnkownCases[j][0]) + abs(allUnkownCases[i][1] - allUnkownCases[j][1]))

    return sum(distances) / len(distances)

def a_star_search_points(graph: SquareGrid, start: GridLocationDirection, goal):
    '''
    but: voir la case goal en gagnant le plus de nouvelles cases possible
    '''
    # startCount = howManyUnknown(graph.map)
    # print("startCount", startCount)

    openList = PriorityQueue()
    openList.put(start, 0)
    came_from: dict[GridLocationDirection, Optional[GridLocationDirection]] = {}
    cost_so_far: dict[GridLocationDirection, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    state_map: dict[GridLocationDirection, List[List[int]]] = {}
    state_map[start] = graph.map
    
    while not openList.empty():
        current: GridLocationDirection = openList.get()
        # print("current", current)
        
        if current[0] == goal[0] and current[1] == goal[1]:
            break

        # print('goal', goal)
        for next in graph.neighbors(current):
            # print("next", next)
            new_cost = cost_so_far[current] + graph.cost(current, next) # every move costs 1 for now
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                # ok on a trouvé une nouvelle route pour aller à next moins chere
                cost_so_far[next] = new_cost
                # update or create nextMap
                # according to next action, new position & potential vision of 3
                newInfos = getAllNewInformation(graph.width, graph.height, state_map[current], next)
                nextMap = updateMap(copy.deepcopy(state_map[current]), newInfos)

                state_map[next] = nextMap

                priority = new_cost + heuristic_pts((next[0], next[1]), goal, nextMap)
                
                openList.put(next, priority)
                came_from[next] = current
                for info in newInfos:
                    if info[0] == goal[0] and info[1] == goal[1]:
                        # print("goal reached")
                        # print(next)
                        return came_from, cost_so_far, next, howManyUnknown(nextMap), getClusteringScore(nextMap)
    return came_from, cost_so_far, None, None

def heuristic_pts(a: GridLocation, goal_pts, map) -> float:
    """
    heuristic for points
    moins il y a de cases à découvrir, plus la valeur est petite
    """
    # return howManyUnknown(map) + abs(a[0] - goal_pts[0]) + abs(a[1] - goal_pts[1])
    return howManyUnknown(map)
