import copy

from enum import Enum

# from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#creating2dLists
def make2dList(rows, cols, val = None):
    s = [ ([None] * cols) for row in range(rows) ]
    for i in range(rows):
        for j in range(cols):
            s[i][j] = copy.deepcopy(val)

    return s

class Direction(Enum):
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    def __invert__(self):
        if self == Direction.NORTH:
            return Direction.SOUTH
        elif self == Direction.SOUTH:
            return Direction.NORTH
        elif self == Direction.WEST:
            return Direction.EAST
        elif self == Direction.EAST:
            return Direction.WEST

class Node:
    def __init__(self):
        self.dirs = []
        self.parent = None

    def __repr__(self):
        return f"Node({self.dirs})"

    def root(self):
        if self.parent == None:
            return self
        else:
            return self.parent.root()

    def connect(self, node):
        node.root().parent = self

    def connected(self, node):
        return node.root() is self.root()