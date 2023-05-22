from typing import List, Tuple
import copy
# no pruning for now

def createMap(n_col : int, n_lig : int):
    """
    Create a map of size n_col * n_lig
    @param n_col: number of columns
    @param n_lig: number of lines
    """
    map = []
    for i in range(n_col):
        map.append([])
        for j in range(n_lig):
            map[i].append(0)
    print(map)
    return map

def isLookingAtABorder(position) -> bool:
    """
    return true if the agent is looking at a border
    @param map: the map of the game
    @param parentPosition: the position of the agent [x, y, direction]
    """
    direction = position[2]
    if direction == 'N':
        if position[1] == 0:
            return True 
    elif direction == 'S':
        if position[1] == (len(GAME_MAP) - 1):
            return True 
    elif direction == 'E':
        if position[0] == (len(GAME_MAP[0]) - 1):
            return True 
    elif direction == 'W':
        if position[0] == 0:
            return True 
    return False

def isOutsideTheMap(coordinates: Tuple[int, int]) -> bool:
    """
    return true if the coordinates are outside the map
    @param coordinates: the coordinates of the cell [x, y]
    """
    if coordinates[0] < 0 or coordinates[1] < 0:
        return True
    if coordinates[0] >= len(GAME_MAP[0]) or coordinates[1] >= len(GAME_MAP):
        return True
    return False

def computePositionBasedOnAction(position, action):
    direction = position[2]
    coordinates = [position[0], position[1]]
    newDirection = direction

    if action == 1:
        # move
        if isLookingAtABorder(position):
            pass
        elif direction == 'N':
            coordinates[1] -= 1
        elif direction == 'S':
            coordinates[1] += 1
        elif direction == 'E':
            coordinates[0] += 1
        elif direction == 'W':
            coordinates[0] -= 1
    elif action == 2:
        # turn 90
        if direction == 'N':
            newDirection = 'E'
        elif direction == 'S':
            newDirection = 'W'
        elif direction == 'E':
            newDirection = 'S'
        elif direction == 'W':
            newDirection = 'N'
    elif action == 3:
        # turn -90
        if direction == 'N':
            newDirection = 'W'
        elif direction == 'S':
            newDirection = 'E'
        elif direction == 'E':
            newDirection = 'N'
        elif direction == 'W':
            newDirection = 'S'

    return coordinates + [newDirection]

# position changes according to the action
def createStateTree(map, position):
    """
    computes the total information gained for each path with DEPTH_MAX depth
    return a list of the values of the total information gained for each path 
    @param map: the map of the game
    @param position: the position of the agent [x, y, direction]
    """
    stateTree = [0]
    positionTree = [position]
    stateMap = [map]
    depthCount = 1
    for _ in range(DEPTH_MAX):
        for _ in range(pow(3, depthCount)):
            parentIndex = (len(stateTree) - 1) // 3
            parentPosition = positionTree[parentIndex]
            parentMap = stateMap[parentIndex]

            # action is 1, 2 or 3
            action = ((len(stateTree) - 1) % 3) + 1

            newPosition = computePositionBasedOnAction(parentPosition, action)
            newInfo = getAllNewInformation(parentMap, newPosition)
            # print("newInfo: " + str(newInfo))
            newMap = updateMap(copy.deepcopy(parentMap), newInfo)

            totalInformationGained = stateTree[parentIndex] + informationGained(newInfo)

            # améliorable en stockant que la derniere position
            stateTree.append(totalInformationGained)
            # améliorable en stockant que la derniere position
            positionTree.append(newPosition)
            # améliorable en stockant que la derniere position
            stateMap.append(newMap)

            # print("----")
            # print("parentIndex: " + str(parentIndex))
            # print("index: " + str(len(stateTree) - 1))
            # print("action: " + str(action))
            # print("newPosition: " + str(newPosition))
            # print("information: " + str(newInfo))
            # print("totalInformationGained: " + str(totalInformationGained))
        depthCount += 1
    return stateTree

def choiceAction(stateTree):
    """
    return the best action to do according to the best path, which maximizes the total information gained
    @param stateTree: list of the values of the total information gained for each path
    """
    lastLevelLeafs = stateTree[len(stateTree) - pow(3, DEPTH_MAX):]
    # print(len(lastLevelLeafs))
    totalPointsForAction1 = sum(lastLevelLeafs[:pow(3, DEPTH_MAX - 1)])
    totalPointsForAction2 = sum(lastLevelLeafs[pow(3, DEPTH_MAX - 1):2 * pow(3, DEPTH_MAX - 1)])
    totalPointsForAction3 = sum(lastLevelLeafs[2 * pow(3, DEPTH_MAX - 1):])
    totalPoints = [totalPointsForAction1, totalPointsForAction2, totalPointsForAction3]

    indexOfTheMaxOfTotal = totalPoints.index(max(totalPoints))
    return indexOfTheMaxOfTotal + 1

def informationGained(newInfo) -> int:
    """
    return the information gained by doing action to the parent value
    +3 if the action reveals may reveal 3 new cells
    +2 if the action reveals may reveal 2 new cells
    +1 if the action reveals may reveal 1 new cells
    0 if we reveal no new cells
    """
    return len(newInfo)

def isInformationAlreadyKnown(map, information) -> bool:
    """
    return true if the information is already known
    @param map: the map of the game
    @param information: the information to check [x, y, value]
    """
    if map[information[1]][information[0]] == information[2]:
        return True
    return False

def getAllNewInformation(map, position) -> List[Tuple[int, int, int]]:
    """
    return all new information the position reveals compared to the map
    @param map: the map of the game
    @param position: the position of the agent [x, y, direction]
    """
    vision = 3
    x = position[0]
    y = position[1]
    direction = position[2]
    computeNewPosition = ["=", "="]
    if direction == 'N':
        computeNewPosition[1] = "-"
    elif direction == 'S':
        computeNewPosition[1] = "+"
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


        if isOutsideTheMap(newPosition): continue
        info = [newPosition[0], newPosition[1], GAME_MAP[newPosition[1]][newPosition[0]]] 
        if isInformationAlreadyKnown(map, info): continue
        
        casesSeen.append(info)
    return casesSeen

def updateMap(map, newInfo):
    """
    update the map with the new information
    @param map: the map of the game
    @param newInfo: the new information to update the map
    """
    for info in newInfo:
        map[info[1]][info[0]] = info[2]
    return map

def turn(map, position):
    stateTree = createStateTree(map, position)
    actionName = None

    print()
    action = choiceAction(stateTree)
    if action == 1:
        actionName = "move"
        print("move")
    elif action == 2:
        actionName = "turn 90"
        print("turn 90")
    elif action == 3:
        actionName = "turn -90"
        print("turn -90")

    newPosition = computePositionBasedOnAction(position, action)
    newInfo = getAllNewInformation(map, newPosition)
    map = updateMap(map, newInfo)
    # print("newPosition: " + str(newPosition))
    # print("newInfo: " + str(newInfo))
    # print("newMap: " + str(map))
    return map, newPosition, actionName

DEPTH_MAX = 8 
GAME_MAP = [
    [5, 2, 4, 2, 1],
    [2, 3, 1, 2, 3],
    [1, 6, 3, 1, 2],
    [7, 1, 1, 2, 3],
    [7, 1, 3, 2, 3],
]
# GAME_MAP = [
#     [5, 2],
#     [2, 3],
# ]
position = [2, 3, 'N']

# map = createMap(5, 5)
map = createMap(5, 5)

print(map)

i = 0
solutionFound = False
actions = []
while i < 35 and not solutionFound:
    map, position, actionName = turn(map, position)
    actions.append(actionName)
    i += 1

    found = False
    for lig in map:
        for cell in lig:
            if cell == 0:
                found = True
    if not found:
        solutionFound = True
print(actions)
print("solutionFound in " + str(i) + " turns: " + str(solutionFound))
