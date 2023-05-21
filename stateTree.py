# no pruning for now
# 3 actions possible: move, turn 90, turn -90
# store at each index the value of the total information gained for this path
# return 1, 2, 3 for the best action
stateTree = []
depth = 0
DEPTH_MAX = 4
count = 0
for i in range(DEPTH_MAX + 1):
    # 3 actions possible
    for j in range(pow(3, depth)):
        stateTree.append(count)
        count += 1
    depth += 1
    # print(stateTree)
# print(stateTree)
# print(count)

def choiceAction(stateTree, DEPTH_MAX):
    # print("indexes last level leafs")
    # print(pow(3, DEPTH_MAX), stateTree[len(stateTree) - pow(3, DEPTH_MAX)])
    # print(len(stateTree) - 1, stateTree[len(stateTree) - 1])

    lastLevelLeafs = stateTree[len(stateTree) - pow(3, DEPTH_MAX):]
    # print("lastLevelLeafs")
    # print(lastLevelLeafs)

    # print("max of lastLevelLeafs")
    # print(max(lastLevelLeafs))
    # print("index of max of lastLevelLeafs")
    # print(lastLevelLeafs.index(max(lastLevelLeafs)))
    indexOfMax = lastLevelLeafs.index(max(lastLevelLeafs))

    # print("tresholds")
    # print(pow(3, DEPTH_MAX - 1), 2 * pow(3, DEPTH_MAX - 1))
    # print(3 * pow(3, DEPTH_MAX - 1))

    if (indexOfMax < pow(3, DEPTH_MAX - 1)):
        return "move"
    elif (indexOfMax < 2 * pow(3, DEPTH_MAX - 1)):
        return 'turn 90'
    return "turn -90"


print("choiceAction")
print(choiceAction(stateTree, DEPTH_MAX))

