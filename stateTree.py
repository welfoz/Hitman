# no pruning for now
# 3 actions possible: move, turn 90, turn -90
# store at each index the value of the total information gained for this path
# return 1, 2, 3 for the best action
DEPTH_MAX = 3

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
    return map

def computePositionBasedOnAction(parentPosition, action):
    newPosition = None
    direction = parentPosition[2]
    if action == 1:
        # move
        if direction == 'N':
            newPosition = [parentPosition[0], parentPosition[1] + 1, direction]
        elif direction == 'S':
            newPosition = [parentPosition[0], parentPosition[1] - 1, direction]
        elif direction == 'E':
            newPosition = [parentPosition[0] + 1, parentPosition[1], direction]
        elif direction == 'W':
            newPosition = [parentPosition[0] - 1, parentPosition[1], direction]
    elif action == 2:
        # turn 90
        if direction == 'N':
            newPosition = [parentPosition[0], parentPosition[1], 'E']
        elif direction == 'S':
            newPosition = [parentPosition[0], parentPosition[1], 'W']
        elif direction == 'E':
            newPosition = [parentPosition[0], parentPosition[1], 'S']
        elif direction == 'W':
            newPosition = [parentPosition[0], parentPosition[1], 'N']
    elif action == 3:
        # turn -90
        if direction == 'N':
            newPosition = [parentPosition[0], parentPosition[1], 'W']
        elif direction == 'S':
            newPosition = [parentPosition[0], parentPosition[1], 'E']
        elif direction == 'E':
            newPosition = [parentPosition[0], parentPosition[1], 'N']
        elif direction == 'W':
            newPosition = [parentPosition[0], parentPosition[1], 'S']
    return newPosition

# position changes according to the action
def createStateTree(map, position):
    """
    computes the total information gained for each path with DEPTH_MAX depth
    return a list of the values of the total information gained for each path 
    @param map: the map of the game
    """

    stateTree = [0]
    positionTree = [position]
    depth = 1
    for i in range(DEPTH_MAX):
        # 3 actions possible
        for j in range(pow(3, depth)):
            parentIndex = (len(stateTree) - 1) // 3
            # action is 1, 2 or 3
            action = ((len(stateTree) - 1) % 3) + 1
            parentPosition = positionTree[parentIndex]

            newPosition = computePositionBasedOnAction(parentPosition, action)
            information = informationGained(map, stateTree[parentIndex], newPosition)

            stateTree.append(information)
            positionTree.append(newPosition)

            print("----")
            print("parentIndex: " + str(parentIndex))
            print("index: " + str(len(stateTree) - 1))
            print("action: " + str(action))
            print("newPosition: " + str(newPosition))
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

def informationGained(map, parentValue, position) -> int:
    """
    return the information gained by doing action to the parent value
    +3 if the action reveals may reveal 3 new cells
    +2 if the action reveals may reveal 2 new cells
    +1 if the action reveals may reveal 1 new cells
    0 if we reveal no new cells
    @param map: the map of the game
    @param parentValue: the value of the total information gained of the parent
    @param position: the position of the agent [x, y]
    """
    return parentValue + 1

stateTree = createStateTree(createMap(4, 3), [0, 0, 'N'])
print(stateTree)
print(len(stateTree))
print("choiceAction")
print(choiceAction(stateTree))

