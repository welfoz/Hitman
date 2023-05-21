# no pruning for now
# 3 actions possible: move, turn 90, turn -90
# store at each index the value of the total information gained for this path
# return 1, 2, 3 for the best action
DEPTH_MAX = 4
def createStateTree():
    stateTree = []
    depth = 0
    count = 0
    for i in range(DEPTH_MAX + 1):
        # 3 actions possible
        for j in range(pow(3, depth)):
            stateTree.append(count)
            count += 1
        depth += 1
    return stateTree


def choiceAction(stateTree):
    """
    return the best action to do
    @param stateTree: list of the values of the total information gained for each path
    """
    lastLevelLeafs = stateTree[len(stateTree) - pow(3, DEPTH_MAX):]
    indexOfMax = lastLevelLeafs.index(max(lastLevelLeafs))

    if (indexOfMax < pow(3, DEPTH_MAX - 1)):
        return "move"
    elif (indexOfMax < 2 * pow(3, DEPTH_MAX - 1)):
        return 'turn 90'
    return "turn -90"

print("choiceAction")
stateTree = createStateTree()
print(choiceAction(stateTree))

