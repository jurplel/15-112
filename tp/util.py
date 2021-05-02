from enum import Enum

import math

from cmu_112_graphics import *

# from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#creating2dLists
def make2dList(rows, cols, val = None):
    return [ ([val] * cols) for row in range(rows) ]

def clamp(x, low, high):
    return max(low, min(x, high))

# for use with lambdas, where you can't assign anything
def modifyDict(d: dict, key, value):
    d[key] = value

# https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbToHex(r, g, b):
    r = clamp(int(r), 0, 255)
    g = clamp(int(g), 0, 255)
    b = clamp(int(b), 0, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

def normAngle(a, deg = False):
    if deg:
        while a > 180:
            a -= 360

        while a < -180:
            a += 360
    else:
        while a > math.pi:
            a -= math.pi*2

        while a < -math.pi:
            a += math.pi*2

    return a


class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        
    def toHex(self):
        return rgbToHex(self.r, self.g, self.b)

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Color(self.r*other, self.g*other, self.b*other)
        else:
            raise TypeError("Must multiply Color by int or float")

    def complementary(self):
        return Color(255-self.r, 255-self.g, 255-self.b)

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

def spritesheetToSprite(spritesheet, rows, cols, height, width, scale = 1, scaleFn = None):
    weaponSprites = [] # 128x128
    for row in range(rows):
        for col in range(cols):
            sprite = spritesheet.crop((width*col, height*row, width*(col+1), height*(row+1))) #ltrb
            if scaleFn != None:
                sprite = scaleFn(sprite, scale)
            img = ImageTk.PhotoImage(sprite)
            weaponSprites.append(img)
    return weaponSprites