# from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#creating2dLists
def make2dList(rows, cols, val = None):
    return [ ([val] * cols) for row in range(rows) ]