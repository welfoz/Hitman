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


def getAllCasesSeenByGuard(position, map) -> List[Tuple[int, int, int]]:
    vision = 2
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
        else: # can't see through objects
            break
    return casesSeen

def getAllGuardsPositions(map) -> List[Tuple[int, int, int]]:
    guardsPositions = []
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] in OBJECTS_INDEX['guard']:
                guardPositionValue = map[y][x]
                direction = None

                # can change with the arbitre
                if guardPositionValue == OBJECTS_INDEX['guard'][1]:
                    direction = 'N'
                elif guardPositionValue == OBJECTS_INDEX['guard'][2]:
                    direction = 'S'
                elif guardPositionValue == OBJECTS_INDEX['guard'][3]:
                    direction = 'E'
                elif guardPositionValue == OBJECTS_INDEX['guard'][4]:
                    direction = 'W'
                
                guardsPositions.append([x, y, direction])
    return guardsPositions

def howManyGuardsLookingAtUs(position, map) -> int:
    guardsPositions = getAllGuardsPositions(map)

    guardsLookingAtUs = 0
    for guardPosition in guardsPositions:
        casesSeen = getAllCasesSeenByGuard(guardPosition, map)
        for caseSeen in casesSeen:
            if caseSeen[0] == position[0] and caseSeen[1] == position[1]:
                guardsLookingAtUs += 1
        
    return guardsLookingAtUs

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
        # farthestCases = self.farthestCasesWithNewInformation(position, map, 1)
        # print(farthestCases)

        diagram = SquareGrid(self.n_col, self.n_lig, map)

        # bestResult = []
        # howManyUnknownBefore = howManyUnknown(map)
        # # bestHowManyUnknown = 100000
        # bestScore = 0
        # bestPath = None

        # for case in farthestCases:
        #     # clusteringScore peut etre utile, à voir comment l'implémenter
        #     path, howManyUnknownVariable, clusteringScore = astar(position, diagram)
        #     result = fromPathToActions(path)

        #     # on favorise les chemins courts, on veut le plus d'info possible par action
        #     score = (howManyUnknownBefore - howManyUnknownVariable) / len(result)

        #     # if howManyUnknownVariable < bestHowManyUnknown: # favorise la découverte
        #     if score > bestScore:
        #         bestScore = score
        #         bestResult = result
        #         bestHowManyUnknown = howManyUnknownVariable
        #         bestPath = path

            # print("----")
            # print("case: " + str(case))
            # print("result: " + str(result))
            # print("howManyUnknownVariable: " + str(howManyUnknownVariable))
            # print("score: " + str(score))
            # print("clusteringScore: " + str(clusteringScore))

        path, howManyUnknownVariable, clusteringScore = astar(position, diagram)
        result = fromPathToActions(path)

        # if howManyUnknownVariable < bestHowManyUnknown: # favorise la découverte
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

    def farthestCasesWithNewInformation(self, position, map, numberOfCasesWanted: int) -> List[Tuple[int, int]]:
        """
        return the X farthest cases with new information
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
        return the manhattan distance between two cases
        @param case1: the first case [x, y]
        @param case2: the second case [x, y]
        """
        return abs(case1[0] - case2[0]) + abs(case1[1] - case2[1])

def astar(start, diagram):
    came_from, cost_so_far, new_goal, howManyUnknown, clusteringScore, backtrack = a_star_search_points(diagram, tuple(start))
    newpathBacktrack = [tuple(start)] + backtrack

    # pprint("newpathBacktrack")
    # pprint(newpathBacktrack)


    if howManyUnknown == None:
        raise Exception("No new goal found")

    if new_goal != None:
        goal = new_goal[0]
        # print("new_goal", new_goal)
    else: 
        raise Exception("No new goal found")

    # new_came_from = {}
    # for key, value in came_from.items():
    #     if value is not None:
    #         if key[0] != value[0] or key[1] != value[1]:
    #             new_came_from[(key[0], key[1])] = (value[0], value[1])
    #     else: 
    #         new_came_from[(key[0], key[1])] = None
    # path = reconstruct_path_new(came_from, start=(tuple(start), None), goal=goal)
    
    # new_cost = {}
    # for key, value in cost_so_far.items():
    #     if value is not None:
    #         new_cost[(key[0], key[1])] = value
    #     else: 
    #         new_cost[(key[0], key[1])] = None
    # print("came_from", came_from)
    # draw_grid(diagram, number=new_cost, start=(start[0], start[1]), goal=goal)
    # draw_gnew_pathrid(diagram, start=(start[0], start[1], start[2]), path=path)
    # new_path = []
    # for case in newpathBacktrack:
    #     new_path.append(case[0])
    
    # pprint(new_path)

    return newpathBacktrack, howManyUnknown, clusteringScore

def reconstruct_path(came_from: dict[str, str], start: str, goal: Tuple[int, int, str]) -> list[str]:
    """
    input: { (0, 0, 'N'): (0, 0, 'N'), (0, 0, 'E', 2): (0, 0, 'N', 1), (1, 0, 'E', 1): (0, 0, 'E', 1) }
    output: [(0, 0, 'N'), (0, 0, 'E'), (1, 0, 'E')]
    """
    current = goal

    path = []

    goalFound = False
    for key in came_from.keys():
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

def a_star_search_points(graph: SquareGrid, start: GridLocationDirection):
    '''
    but: voir la case goal en gagnant le plus de nouvelles cases possible

    explosion en mémoire on stocke bcp de trucs
    a t on besoin de tout stocker ?
    '''
    openList = PriorityQueue()
    startTuple = (start, None)
    openList.put(startTuple, 0)
    
    came_from: dict[Tuple[GridLocationDirection, Optional[GridLocationDirection]], Tuple[Optional[GridLocationDirection], Optional[GridLocationDirection]]] = {}
    cost_so_far: dict[Tuple[GridLocationDirection, Optional[GridLocationDirection]], Tuple[float, float, float]] = {}
    came_from[startTuple]= None, None
    cost_so_far[startTuple] = (0, howManyUnknown(graph.map), 0)
    state_map: dict[Tuple[GridLocationDirection, Optional[GridLocationDirection]], List[List[int]]] = {}
    state_map[startTuple] = graph.map

    minimum = start
    minimumValue = howManyUnknown(graph.map)

    previous = {}
    previous[startTuple] = (None, None)

    minimumCostPosition = start
    minimumCostValue = 10000

    backtrack = {}
    backtrack[startTuple] = []

    count = 0
    MAX = 30000
    while not openList.empty():
        count += 1
        current: Tuple[GridLocationDirection, Optional[GridLocationDirection]] = openList.get()

        if backtrack.get(current, None) == None:
            backtrack[current] = []
        
        # if we have multiple minimums equals (= 0, =1....)
        # then we take the one with the minimum cost
        if cost_so_far[current][1] < minimumValue \
                or (cost_so_far[current][1] == minimumValue and cost_so_far[current][0] < minimumCostValue):
            minimum = current
            minimumValue = cost_so_far[current][1]
            minimumCostValue = cost_so_far[current][0]
            minimumCostPosition = current

        if howManyUnknown(state_map[current]) == 0:
            # the first solution is the best one if we have a good heuristic
            print("goal found")
            break

        for next in graph.neighbors(current[0]):
            nextTuple = (next, current[0])

            newInfos = getAllNewInformation(graph.width, graph.height, state_map[current], next)
            nextMap = updateMap(copy.deepcopy(state_map[current]), newInfos)
            # new_cost = cost_so_far[current][0] + 1 #graph.cost(current, next) # every move costs 1 for now
            howManyGuardsAreSeeingUs = howManyGuardsLookingAtUs(next, graph.map)
            new_cost = cost_so_far[current][0] + graph.cost(howManyGuardsAreSeeingUs) # default cost = 2, if we know a guard is seeing us, cost = 2 + 5*guards seeing us
            # score is the number of newInfos / the cost
            # goal: minimize the cost and maximize the number of newInfos
            # score means ratio combien de nouvelle info par action
            howManyNewInfosSinceBeginning = howManyUnknown(graph.map) - howManyUnknown(nextMap)
            score = howManyNewInfosSinceBeginning / new_cost
            if nextTuple not in cost_so_far or howManyUnknown(nextMap) < cost_so_far[nextTuple][1] or (howManyUnknown(nextMap) == cost_so_far[nextTuple][1] and new_cost < cost_so_far[nextTuple][0]): # on a trouvé une nouvelle route pour aller à nextTuple moins chere
                # si on trouve une route apportant plus d'information pour aller à nextTuple, on la prend
                backtrack[nextTuple] = backtrack[current] + [nextTuple[0]]

                cost_so_far[nextTuple] = (new_cost, howManyUnknown(nextMap), score)

                state_map[nextTuple] = nextMap

                priority = new_cost + howManyUnknown(nextMap) # pretty efficient but not best result
                # priority = howManyUnknown(nextMap) # pretty efficient but not best result
                # priority = new_cost + score # inneficient but find the best result as it expends more than others
                # priority = new_cost + score * 10 # get stuck, why ? circular path
                # priority = new_cost # diskstra
                
                openList.put(nextTuple, priority)
                # to test
                came_from[nextTuple] = current[0], previous[current][0]
                previous[nextTuple] = current
    print("total count: ", count)
    print('len nodes: ', len(list(cost_so_far.keys())))

    return came_from, cost_so_far, (minimumCostPosition, previous[minimumCostPosition]), minimumValue, getClusteringScore(state_map[minimum]), backtrack[minimumCostPosition]

def heuristic_pts(map) -> float:
    """
    heuristic for points
    moins il y a de cases à découvrir, plus la valeur est petite
    """
    return howManyUnknown(map)

def reconstruct_path_new(
        came_from: dict[
            Tuple[GridLocationDirection, Optional[GridLocationDirection]],
            Tuple[Optional[GridLocationDirection], Optional[GridLocationDirection]]
            ], 
        start: Tuple[GridLocationDirection, None], goal: Tuple[GridLocationDirection, Optional[GridLocationDirection]]) -> list[str]:
    """
    input: { (0, 0, 'N'): (0, 0, 'N'), (0, 0, 'E', 2): (0, 0, 'N', 1), (1, 0, 'E', 1): (0, 0, 'E', 1) }
    output: [(0, 0, 'N'), (0, 0, 'E'), (1, 0, 'E')]
    """
    current = goal

    path = []

    goalFound = False
    for key in came_from.keys():
        if key[0] == goal[0] and key[1] == goal[1]:
            print("key 0", key[0])
            print("key 1", key[1])
            goalFound = True
            break
    if not goalFound:
        return []

    MAX = 1000
    count = 0
    while current != start and count < MAX:
        path.append(current)
        current = came_from[current]
        count += 1
    if count == MAX:
        print("MAX")
        raise Exception("MAX")
    path.append(start) # optional
    path.reverse() # optional
    return path
