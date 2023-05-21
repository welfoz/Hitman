from typing import List, Tuple
# no pruning for now
# 3 actions possible: move, turn 90, turn -90
# store at each index the value of the total information gained for this path
# return 1, 2, 3 for the best action
DEPTH_MAX = 2
GAME_MAP = [
    [5, 2, 4],
    [2, 3, 1],
    [1, 6, 3],
    [7, 1, 1],
]

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

# mal nommmée
def isOnABorder(parentPosition) -> bool:
    """
    return true if the position is on a border of the map
    @param map: the map of the game
    @param parentPosition: the position of the agent [x, y, direction]
    """
    direction = parentPosition[2]
    if direction == 'N':
        if parentPosition[1] == 0:
            return True 
    elif direction == 'S':
        if parentPosition[1] == (len(GAME_MAP) - 1):
            return True 
    elif direction == 'E':
        if parentPosition[0] == (len(GAME_MAP[0]) - 1):
            return True 
    elif direction == 'W':
        if parentPosition[0] == 0:
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


def computePositionBasedOnAction(map, parentPosition, action):
    direction = parentPosition[2]

    if action == 1:
        # move
        if isOnABorder(parentPosition): return parentPosition

        if direction == 'N':
            return [parentPosition[0], parentPosition[1] - 1, direction]
        elif direction == 'S':
            return [parentPosition[0], parentPosition[1] + 1, direction]
        elif direction == 'E':
            return [parentPosition[0] + 1, parentPosition[1], direction]
        elif direction == 'W':
            return [parentPosition[0] - 1, parentPosition[1], direction]
    elif action == 2:
        # turn 90
        if direction == 'N':
            return [parentPosition[0], parentPosition[1], 'E']
        elif direction == 'S':
            return [parentPosition[0], parentPosition[1], 'W']
        elif direction == 'E':
            return [parentPosition[0], parentPosition[1], 'S']
        elif direction == 'W':
            return [parentPosition[0], parentPosition[1], 'N']
    elif action == 3:
        # turn -90
        if direction == 'N':
            return [parentPosition[0], parentPosition[1], 'W']
        elif direction == 'S':
            return [parentPosition[0], parentPosition[1], 'E']
        elif direction == 'E':
            return [parentPosition[0], parentPosition[1], 'N']
        elif direction == 'W':
            return [parentPosition[0], parentPosition[1], 'S']

    return None

# position changes according to the action
def createStateTree(map, position):
    """
    computes the total information gained for each path with DEPTH_MAX depth
    return a list of the values of the total information gained for each path 
    @param map: the map of the game
    """

    stateTree = [0]
    positionTree = [position]
    stateMap = [map]
    depth = 1
    for i in range(DEPTH_MAX):
        # 3 actions possible
        for j in range(pow(3, depth)):
            parentIndex = (len(stateTree) - 1) // 3
            # action is 1, 2 or 3
            action = ((len(stateTree) - 1) % 3) + 1
            parentPosition = positionTree[parentIndex]

            newPosition = computePositionBasedOnAction(map, parentPosition, action)
            # pnt est ce que faut stocker toutes les stateMaps parents ou meme juste la derniere
            # on est obligé de comparé l'information de la nouvelle position avec la derniere position
            # information is [x, y, value]
            newInfo = newInformation(map, newPosition)
            totalInformationGained = stateTree[parentIndex] + informationGained(newInfo)

            # améliorable en stockant que la derniere position
            stateTree.append(totalInformationGained)
            # améliorable en stockant que la derniere position
            positionTree.append(newPosition)
            # stateMap.append(newMap)

            print("----")
            print("parentIndex: " + str(parentIndex))
            print("index: " + str(len(stateTree) - 1))
            print("action: " + str(action))
            print("newPosition: " + str(newPosition))
            print("information: " + str(newInfo))
            print("totalInformationGained: " + str(totalInformationGained))
        depth += 1
    return stateTree

def choiceAction(stateTree):
    """
    return the best action to do according to the best path, which maximizes the total information gained
    @param stateTree: list of the values of the total information gained for each path
    """
    lastLevelLeafs = stateTree[len(stateTree) - pow(3, DEPTH_MAX):]
    print(len(lastLevelLeafs))
    indexOfMax = lastLevelLeafs.index(max(lastLevelLeafs))

    if (indexOfMax < pow(3, DEPTH_MAX - 1)):
        return "move"
    elif (indexOfMax < 2 * pow(3, DEPTH_MAX - 1)):
        return 'turn 90'
    return "turn -90"

def informationGained(newInfo) -> int:
    """
    return the information gained by doing action to the parent value
    +3 if the action reveals may reveal 3 new cells
    +2 if the action reveals may reveal 2 new cells
    +1 if the action reveals may reveal 1 new cells
    0 if we reveal no new cells
    """
    if len(newInfo) == 3:
        return 3
    elif len(newInfo) == 2:
        return 2
    elif len(newInfo) == 1:
        return 1
    return 0

def isInformationAlreadyKnown(map, information) -> bool:
    """
    return true if the information is already known
    @param map: the map of the game
    @param information: the information to check [x, y, value]
    """
    if map[information[1]][information[0]] == information[2]:
        return True
    return False

def newInformation(map, position) -> List[Tuple[int, int, int]]:
    """
    return all new information the position reveals compared to the map
    @param map: the map of the game
    @param position: the position of the agent [x, y, direction]
    """
    x = position[0]
    y = position[1]
    direction = position[2]
    vision = 3
    casesLookedAt = []
    if direction == 'N':
        for i in range(vision):
            newPosition = [x, y - i - 1]
            if isOutsideTheMap(newPosition): continue

            info = [x, y - i - 1, GAME_MAP[y - i - 1][x]]
            if isInformationAlreadyKnown(map, info): continue
            casesLookedAt.append(info)
    elif direction == 'S':
        for i in range(vision):
            newPosition = [x, y + i + 1]
            if isOutsideTheMap(newPosition): continue
            info = [x, y + i + 1, GAME_MAP[y + i + 1][x]]
            if isInformationAlreadyKnown(map, info): continue
            casesLookedAt.append(info)
    elif direction == 'E':
        for i in range(vision):
            newPosition = [x + i + 1, y]
            if isOutsideTheMap(newPosition): continue
            info = [x + i + 1, y, GAME_MAP[y][x + i + 1]]
            if isInformationAlreadyKnown(map, info): continue
            casesLookedAt.append(info)
    elif direction == 'W':
        for i in range(vision):
            newPosition = [x - i - 1, y]
            if isOutsideTheMap(newPosition): continue
            info = [x - i - 1, y, GAME_MAP[y][x - i - 1]]
            if isInformationAlreadyKnown(map, info): continue
            casesLookedAt.append(info)

    return casesLookedAt


# stateTree = createStateTree(createMap(4, 3), [0, 0, 'S'])
map = [
    [0, 0, 0],
    [0, 0, 0],
    [1, 0, 0],
    [7, 0, 0]
]
print(map)
stateTree = createStateTree(map, [0, 0, 'S'])
print(stateTree)
print(len(stateTree))
print("choiceAction")
print(choiceAction(stateTree))

