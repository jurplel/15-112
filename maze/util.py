# from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#creating2dLists

dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]

def make2dList(rows, cols, val = None):
    return [ ([val] * cols) for row in range(rows) ]