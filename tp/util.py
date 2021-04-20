# from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#creating2dLists
def make2dList(rows, cols, val = None):
    return [ ([val] * cols) for row in range(rows) ]

def clamp(x, low, high):
    return max(low, min(x, high))

# https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbToHex(r, g, b):
    r = clamp(int(r), 0, 255)
    g = clamp(int(g), 0, 255)
    b = clamp(int(b), 0, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

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