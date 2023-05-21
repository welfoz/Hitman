# no pruning for now
# 3 actions possible: move, turn 90, turn -90
# store at each index the value of the total information gained for this path
# return 1, 2, 3 for the best action
DEPTH_MAX = 2

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

def createStateTree(map):
    """
    computes the total information gained for each path with DEPTH_MAX depth
    return a list of the values of the total information gained for each path 
    @param map: the map of the game
    """

    stateTree = [0]
    depth = 1
    for i in range(DEPTH_MAX):
        # 3 actions possible
        for j in range(pow(3, depth)):
            parentIndex = (len(stateTree) - 1) // 3
            print("parentIndex: " + str(parentIndex))
            stateTree.append(informationGained(map, stateTree[parentIndex]))
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

def informationGained(map, parentValue) -> int:
    """
    return the information gained by doing action
    @param map: the map of the game
    @param action: the action to do
    """
    return parentValue + 1

stateTree = createStateTree(createMap(4, 3))
print(stateTree)
print(len(stateTree))
print("choiceAction")
print(choiceAction(stateTree))

