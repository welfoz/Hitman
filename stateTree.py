from typing import List, Tuple
import copy
import random

OBJECTS_INDEX = {
    'empty': 1,
    'wall': 2,
    'target': 3,
    'rope': 4,
    'costume': 5,
    'guard': [6, 7, 8, 9, 10], # 6 default, 7: north, 8: south, 9: east, 10: west
    'civil': [11, 12, 13, 14, 15], # 11 default, 12: north, 13: south, 14: east, 15: west
}


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

def isLookingAtAnImpassableObstacle(position) -> bool:
    x = position[0]
    y = position[1]
    direction = position[2]
    newPositionValue = None

    if direction == 'N':
        # same, we cant know
        newPositionValue = GAME_MAP[y - 1][x]
    elif direction == 'S':
        newPositionValue = GAME_MAP[y + 1][x]
    elif direction == 'E':
        newPositionValue = GAME_MAP[y][x + 1]
    elif direction == 'W':
        newPositionValue = GAME_MAP[y][x - 1]

    if newPositionValue == OBJECTS_INDEX['wall'] or newPositionValue in OBJECTS_INDEX['guard']:
        return True
    return False

def computePositionBasedOnAction(position, action):
    direction = position[2]
    coordinates = [position[0], position[1]]
    newDirection = direction

    if action == 1:
        # move
        if isLookingAtABorder(position) or isLookingAtAnImpassableObstacle(position):
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
            # we can't use this function because we don't know the new map, the referee doesn't give us the information
            # we just can hope the amount of new information we have
            newInfo = getAllNewInformation(parentMap, newPosition)
            # print("newInfo: " + str(newInfo))
            newMap = updateMap(copy.deepcopy(parentMap), newInfo)

            # we don't know the new map by computing the new position
            # l'arbitre ne nous donne pas l'info
            totalInformationGained = stateTree[parentIndex] + informationGained(newPosition, newInfo, map)

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

def choiceAction(stateTree: List[int]):
    """
    return the best action to do according to the best path, which maximizes the total information gained
    @param stateTree: list of the values of the total information gained for each path
    """
    lastLevelLeafs = stateTree[len(stateTree) - pow(3, DEPTH_MAX):]
    # print(len(lastLevelLeafs))
    # print(lastLevelLeafs)

    lastLevelLeafsMAX = max(lastLevelLeafs)
    howManyMax = lastLevelLeafs.count(lastLevelLeafsMAX)

    # print("lastLevelLeafsMAX: " + str(lastLevelLeafsMAX))

    count1 = 0
    count2 = 0
    count3 = 0
    # lastLevelLeafs1 = lastLevelLeafs[:pow(3, DEPTH_MAX - 1)]
    # lastLevelLeafs2 = lastLevelLeafs[pow(3, DEPTH_MAX - 1):2 * pow(3, DEPTH_MAX - 1)]
    # lastLevelLeafs3 = lastLevelLeafs[2 * pow(3, DEPTH_MAX - 1):]
    # print("lastLevelLeafs1: " + str(lastLevelLeafs1))
    # print("lastLevelLeafs2: " + str(lastLevelLeafs2))
    # print("lastLevelLeafs3: " + str(lastLevelLeafs3))
    while lastLevelLeafs.count(lastLevelLeafsMAX) > 0:
        firstIndexMax = lastLevelLeafs.index(lastLevelLeafsMAX)
        # print("firstIndexMax: " + str(firstIndexMax))
        if firstIndexMax < pow(3, DEPTH_MAX - 1):
            count1 += 1
        elif firstIndexMax < 2 * pow(3, DEPTH_MAX - 1):
            count2 += 1
        else:
            count3 += 1
        lastLevelLeafs[firstIndexMax] = -1000
    # print("count1: " + str(count1))
    # print("count2: " + str(count2))
    # print("count3: " + str(count3))

    proba1 = count1 / howManyMax
    proba2 = count2 / howManyMax
    proba3 = count3 / howManyMax

    # print("proba1: " + str(proba1))
    # print("proba2: " + str(proba2))
    # print("proba3: " + str(proba3))


    # test this for now
    # lets see how it goes
    return random.choices([1, 2, 3], [proba1, proba2, proba3])[0]

def getAllCasesSeenByGuard(position) -> List[Tuple[int, int, int]]:
    vision = 2
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

        casesSeen.append(info)

        # if case not empty, vision stops here
        if info[2] != OBJECTS_INDEX['empty']: 
            break
    return casesSeen

def getAllGuardsPositions(map: List[List[int]]) -> List[Tuple[int, int, int]]:
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

    # false, we don't know yet
    guardsLookingAtUs = 0
    for guardPosition in guardsPositions:
        casesSeen = getAllCasesSeenByGuard(guardPosition)
        for caseSeen in casesSeen:
            if caseSeen[0] == position[0] and caseSeen[1] == position[1]:
                guardsLookingAtUs += 1
        
    return guardsLookingAtUs

def informationGained(position, newInfo, map) -> int:
    """
    return the information gained by doing action to the parent value
    """
    newCases = len(newInfo)
    penalty = howManyGuardsLookingAtUs(position, map) * 5

    return newCases * 2 - penalty

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

        if not isInformationAlreadyKnown(map, info):
            casesSeen.append(info)

        # if case not empty, vision stops here
        if info[2] != OBJECTS_INDEX['empty']: 
            break
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
    print("newPosition: " + str(newPosition))
    print("newInfo: " + str(newInfo))
    print("Map: " + str(map))
    map = updateMap(map, newInfo)
    print("newMap: " + str(map))
    return map, newPosition, actionName

DEPTH_MAX = 4
# GAME_MAP = [
#     [5, 2, 4, 2, 1],
#     [2, 3, 1, 2, 3],
#     [1, 6, 3, 1, 2],
#     [7, 1, 1, 2, 3],
#     [7, 1, 3, 2, 3],
# ]
GAME_MAP = [
    [5, 2, 1, 7, 1],
    [1, 1, 5, 8, 1],
    [7, 1, 5, 3, 1],
]
# position = [2, 3, 'N']
position = [0, 0, 'N']

# map = createMap(5, 5)
map = createMap(3, 5)
# do we have this ?
map[0][0] = 5

print(map)

i = 0
solutionFound = False
actions = []
while i < 40 and not solutionFound:
    map, position, actionName = turn(map, position)
    actions.append([actionName, position])
    i += 1

    found = False
    for lig in map:
        for cell in lig:
            if cell == 0:
                found = True
    if not found:
        solutionFound = True
for a in actions:
    print(a)
print("solutionFound in " + str(i) + " turns: " + str(solutionFound))
