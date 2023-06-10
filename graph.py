"""
use graph to represent states and actions in the game
and use BFS and A star to search the path

"""
from typing import List, Dict, Tuple, Optional
from pprint import pprint

class Node: 
    def __init__(self, state, action, cost, discoveries, parent = None):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.discoveries = discoveries
        self.childs: List[Node] = []

    def __repr__(self):
        return f"Node({self.state}, {self.action}, {self.cost}, {self.discoveries}, {self.childs})"

    def getParentsActions(self):
        if self.parent == None:
            return [self.action]
        else:
            return self.parent.getParentsActions() + [self.action]
        
    def allChilds(self):
        if self.childs == []:
            return []
        else:
            return self.childs + [child.allChilds() for child in self.childs]
    
    def addChild(self, child):
        # self.childs.append(Node(
        #     parent = self,
        #     action = child["action"],
        #     cost = child["cost"],
        #     discoveries = child["discoveries"],
        #     state = child["state"]
        # ))
        self.childs.append(child)

        
    # def __eq__(self, other):
    #     return self.state == other.state

    # def __hash__(self):
    #     return hash(self.state)

    # def __lt__(self, other):
    #     return self.cost < other.cost

    # def __gt__(self, other):
    #     return self.cost > other.cost
parentNode = Node(
    action = None,
    cost = 0,
    discoveries = [],
    state = {
        "me": (1, 1),
    }
)
child = {
    'action' : "up",
    'cost' : 1,
    'discoveries' : [],
    'state' : {
        "me": (1, 2),
    }
}
superChild = Node(
    parent = parentNode,
    action = "up",
    cost = 2,
    discoveries = [],
    state = {
        "me": (1, 3),
    }
)

## construct the graph
# parentNode.addChild(child)
# parentNode.addChild(child)
# parentNode.addChild(child)
parentNode.addChild(superChild)
parentNode.addChild(superChild)
parentNode.addChild(superChild)



pprint(parentNode)
pprint(parentNode.allChilds())
# print(child)

# print(child.getParents())
# print(superChild.getParentsActions())
