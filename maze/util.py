from enum import Enum

# from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#creating2dLists
def make2dList(rows, cols, val = None):
    return [ ([val] * cols) for row in range(rows) ]

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