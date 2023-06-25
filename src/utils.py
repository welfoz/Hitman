
from typing import List, Tuple, Dict
from src.aliases import OBJECTS_INDEX, Information, Orientation, Information, OBJECTS_INDEX
from arbitre_gitlab.hitman.hitman import HC

""" dans arbitre :
from maps import world_examples

class HitmanReferee:
    def __init__(self, map_int: int) -> None:
        self.__map_int = map_int
        self.__world = world_examples[map_int]
        self.__m = len(self.__world)
        self.__n = len(self.__world[0])
        """

def addTurnInfo(status, heardMap, seenMap, map):
    visions = getVisionsFromStatus(status["vision"])
    # print("visions", visions)
    for vision in visions: 
        if (not isInformationAlreadyKnown(map, vision)):
            map = updateMap(map, [vision])

    if status["is_in_guard_range"]:
        seenInfo = 1
    else:
        seenInfo = 0
    if (not isInformationAlreadyKnown(seenMap, (status["position"][0], status["position"][1], seenInfo))):
        seenMap = updateMap(seenMap, [(status["position"][0], status["position"][1], seenInfo)])

    heardInfo: Information = [status["position"][0], status["position"][1], status["hear"]]
    if (not isInformationAlreadyKnown(heardMap, heardInfo)):
        heardMap = updateMap(heardMap, [heardInfo])
    return

def findObject(map, object):
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] == object:
                return (j, i)
    return None

def isInCase(position, goal):
    if (position[0], position[1]) == (goal[0], goal[1]):
        return True
    return False

def HCInfoToObjectIndexFull(value : int) -> int:
     if value == HC.GUARD_N._value_:
         return OBJECTS_INDEX['guard'][1]
     if value == HC.GUARD_S._value_:
         return OBJECTS_INDEX['guard'][2]
     if value == HC.GUARD_E._value_:
         return OBJECTS_INDEX['guard'][3]
     if value == HC.GUARD_W._value_:
         return OBJECTS_INDEX['guard'][4]
     if value == HC.CIVIL_N._value_:
         return OBJECTS_INDEX['civil'][1]
     if value == HC.CIVIL_S._value_:
         return OBJECTS_INDEX['civil'][2]
     if value == HC.CIVIL_E._value_:
         return OBJECTS_INDEX['civil'][3]
     if value == HC.CIVIL_W._value_:
         return OBJECTS_INDEX['civil'][4]
     if value == HC.EMPTY._value_:
         return OBJECTS_INDEX['empty']
     if value == HC.WALL._value_:
         return OBJECTS_INDEX['wall']
     if value == HC.TARGET._value_:
         return OBJECTS_INDEX['target']
     if value == HC.SUIT._value_:
         return OBJECTS_INDEX['costume']
     if value == HC.PIANO_WIRE._value_:
         return OBJECTS_INDEX['rope']

def getVisionsFromStatus(status_vision: List[Tuple[Tuple[int, int], HC]]) -> List[Information]:
    visions = []
    for vision in status_vision:
        visionValue = HCInfoToObjectIndexFull(vision[1].value)
        visions.append([vision[0][0], vision[0][1], visionValue])
    return visions

def updateSolutionMap(solutionMap: Dict[Tuple[int, int], HC], vision: List[Tuple[Tuple[int, int], HC]]) -> Dict[Tuple[int, int], HC]:
    for v in vision:
        solutionMap[(v[0][0], v[0][1])] = v[1]
    return solutionMap

def fromHCDirectionToOrientation(direction: HC) -> Orientation:
    if direction == HC.N:
        return "N"
    elif direction == HC.S:
        return "S"
    elif direction == HC.E:
        return "E"
    elif direction == HC.W:
        return "W"
    raise Exception("Unknown direction")

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
    # print(map)
    return map

def isInformationAlreadyKnown(map, information: Information) -> bool:
    """
    return true if the information is already known
    @param map: the map of the game
    @param information: the information to check [x, y, value]
    """
    if map[information[1]][information[0]] == information[2]:
        return True
    return False

def isOutsideTheMap(n_col, n_lig, coordinates: Tuple[int, int]) -> bool:
    """
    return true if the coordinates are outside the map
    @param coordinates: the coordinates of the cell [x, y]
    """
    if coordinates[0] < 0 or coordinates[1] < 0:
        return True
    if coordinates[0] >= n_col or coordinates[1] >= n_lig:
        return True
    return False

def getAllNewInformation(n_col, n_lig, map, position) -> List[Tuple[int, int, int]]:
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

        if isOutsideTheMap(n_col, n_lig, newPosition): continue

        info = [newPosition[0], newPosition[1], map[newPosition[1]][newPosition[0]]] 

        if info[2] == OBJECTS_INDEX['empty']: # can see through empty cells
            casesSeen.append(info)
        elif info[2] == -1: # unknown cell
            info[2] = -2 # means we don't know what we see
            casesSeen.append(info)
        elif info[2] != OBJECTS_INDEX['empty']: # can't see through objects
            break

    return casesSeen

def howManyUnknown(map: List[List[int]]) -> int:
    unknown = 0
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] == -1:
                unknown += 1
    return unknown

def isMapComplete(map: List[List[HC]]) -> bool:
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] == -1:
                return False
    return True
