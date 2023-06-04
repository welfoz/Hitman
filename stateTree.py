from typing import List, Tuple
import copy
import random

from aliases import Position, OBJECTS_INDEX, Information


class ActionChoice:
    def __init__(self, n_col, n_lig):
        self.n_col = n_col 
        self.n_lig = n_lig
        self.depth_max = 6

    def isLookingAtABorder(self, position) -> bool:
        """
        return true if the agent is looking at a border
        @param map: the map of the game
        @param parentPosition: the position of the agent [x, y, direction]
        """
        direction = position[2]
        if direction == 'N':
            if position[1] == self.n_lig - 1:
                return True 
        elif direction == 'S':
            if position[1] == 0:
                return True 
        elif direction == 'E':
            if position[0] == self.n_col - 1:
                return True 
        elif direction == 'W':
            if position[0] == 0:
                return True 
        return False

    def isOutsideTheMap(self, coordinates: Tuple[int, int]) -> bool:
        """
        return true if the coordinates are outside the map
        @param coordinates: the coordinates of the cell [x, y]
        """
        if coordinates[0] < 0 or coordinates[1] < 0:
            return True
        if coordinates[0] >= self.n_col or coordinates[1] >= self.n_lig:
            return True
        return False

    def isLookingAtAnImpassableObstacle(self, position, map) -> bool:
        x = position[0]
        y = position[1]
        direction = position[2]
        newPositionValue = None

        if direction == 'N':
            newPositionValue = map[y + 1][x]
        elif direction == 'S':
            newPositionValue = map[y - 1][x]
        elif direction == 'E':
            newPositionValue = map[y][x + 1]
        elif direction == 'W':
            newPositionValue = map[y][x - 1]

        if newPositionValue == OBJECTS_INDEX['wall'] or newPositionValue in OBJECTS_INDEX['guard']:
            return True
        return False

    def computePositionBasedOnAction(self, position: Position, action, map)-> Position:
        direction = position[2]
        coordinates = [position[0], position[1]]
        newDirection = direction

        if action == 1:
            # move
            if self.isLookingAtABorder(position) or self.isLookingAtAnImpassableObstacle(position, map):
                pass
            elif direction == 'N':
                coordinates[1] += 1
            elif direction == 'S':
                coordinates[1] -= 1
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
    def createStateTree(self, map, position: Position):
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
        for _ in range(self.depth_max):
            for _ in range(pow(3, depthCount)):
                parentIndex = (len(stateTree) - 1) // 3
                parentPosition = positionTree[parentIndex]
                parentMap = stateMap[parentIndex]

                # action is 1, 2 or 3
                action = ((len(stateTree) - 1) % 3) + 1

                newPosition = self.computePositionBasedOnAction(parentPosition, action, parentMap)

                newInfo = self.getAllNewInformation(parentMap, newPosition)
                # print("newPosition: " + str(newPosition))
                # print("newInfo: " + str(newInfo))
                newMap = updateMap(copy.deepcopy(parentMap), newInfo)
                # print("newMap: " + str(newMap))

                if newPosition == parentPosition:
                    totalInformationGained = -10000
                else:
                    totalInformationGained = stateTree[parentIndex] + self.informationGained(newPosition, newInfo, map)

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

    def choose(self, map, position):
        """
        return the best action to do according to the best path, which maximizes the total information gained
        @param stateTree: list of the values of the total information gained for each path
        """
        stateTree = self.createStateTree(map, position)
        beforeLastLevelLeafs = stateTree[:len(stateTree) - pow(3, self.depth_max)]
        lastLevelLeafs = stateTree[len(stateTree) - pow(3, self.depth_max):]
        # print(len(lastLevelLeafs))
        # print(lastLevelLeafs)
        # totalPointsForAction1 = sum(lastLevelLeafs[:pow(3, self.depth_max - 1)])
        # totalPointsForAction2 = sum(lastLevelLeafs[pow(3, self.depth_max - 1):2 * pow(3, self.depth_max - 1)])
        # totalPointsForAction3 = sum(lastLevelLeafs[2 * pow(3, self.depth_max - 1):])
        # totalPoints = [totalPointsForAction1, totalPointsForAction2, totalPointsForAction3]

        # indexOfTheMaxOfTotal = totalPoints.index(max(totalPoints))
        # return indexOfTheMaxOfTotal + 1
        # print(len(lastLevelLeafs))
        print(beforeLastLevelLeafs)
        print(lastLevelLeafs)

        lastLevelLeafsMAX = max(lastLevelLeafs)
        howManyMax = lastLevelLeafs.count(lastLevelLeafsMAX)

        print()
        print("evaluation funciton: ")
        print("lastLevelLeafsMAX: " + str(lastLevelLeafsMAX))

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
            if firstIndexMax < pow(3, self.depth_max - 1):
                count1 += 1
            elif firstIndexMax < 2 * pow(3, self.depth_max - 1):
                count2 += 1
            else:
                count3 += 1
            lastLevelLeafs[firstIndexMax] = -1000
        print("count1: " + str(count1), end=" ")
        print("count2: " + str(count2), end=" ")
        print("count3: " + str(count3))


        proba1 = count1 / howManyMax
        proba2 = count2 / howManyMax
        proba3 = count3 / howManyMax

        print("proba1: " + str(proba1), end=" ")
        print("proba2: " + str(proba2), end=" ")
        print("proba3: " + str(proba3), end=" ")
        print()
        print()

        # test this for now
        # lets see how it goes
        return random.choices([1, 2, 3], [proba1, proba2, proba3])[0]

    def getAllCasesSeenByGuard(self, position, map) -> List[Tuple[int, int, int]]:
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

            if self.isOutsideTheMap(newPosition): continue
            info = [newPosition[0], newPosition[1], map[newPosition[1]][newPosition[0]]] 

            casesSeen.append(info)

            # if case not empty, vision stops here
            if info[2] != OBJECTS_INDEX['empty']: 
                break
        return casesSeen

    def getAllGuardsPositions(self, map) -> List[Tuple[int, int, int]]:
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

    def howManyGuardsLookingAtUs(self, position, map) -> int:
        guardsPositions = self.getAllGuardsPositions(map)

        guardsLookingAtUs = 0
        for guardPosition in guardsPositions:
            casesSeen = self.getAllCasesSeenByGuard(guardPosition, map)
            for caseSeen in casesSeen:
                if caseSeen[0] == position[0] and caseSeen[1] == position[1]:
                    guardsLookingAtUs += 1
            
        return guardsLookingAtUs

    def informationGained(self, position, newInfo, map) -> int:
        """
        return the information gained by doing action to the parent value
        """
        newCases = len(newInfo)
        # penalty = self.howManyGuardsLookingAtUs(position, map) * 5

        # for now we don't take into account the penalty
        # return newCases * 2 - penalty
        return newCases

    def getAllNewInformation(self, map, position) -> List[Tuple[int, int, int]]:
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


            if self.isOutsideTheMap(newPosition): continue
            # info = [newPosition[0], newPosition[1], map[newPosition[1]][newPosition[0]]] 
            info = [newPosition[0], newPosition[1], 1] 

            # if not isInformationAlreadyKnown(map, info):
            if map[newPosition[1]][newPosition[0]] == -1:
                casesSeen.append(info)
            else:
                if map[newPosition[1]][newPosition[0]] != OBJECTS_INDEX['empty']:
                    break

        return casesSeen

def isInformationAlreadyKnown(map, information: Information) -> bool:
    """
    return true if the information is already known
    @param map: the map of the game
    @param information: the information to check [x, y, value]
    """
    if map[information[1]][information[0]] == information[2]:
        return True
    return False

def updateMap(map, newInfo: Information):
    """
    update the map with the new information
    @param map: the map of the game
    @param newInfo: the new information to update the map
    """
    for info in newInfo:
        map[info[1]][info[0]] = info[2]
    return map

def createMap(n_col, n_lig):
    """
    Create a map of size n_col * n_lig
    @param n_col: number of columns
    @param n_lig: number of lines
    """
    map = []
    for i in range(n_lig):
        map.append([])
        for _ in range(n_col):
            map[i].append(-1)
    print(map)
    return map

