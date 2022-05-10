from util import make2dList

class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.history = []
        self.maze = make2dList(rows, cols, None)
        self.done = False

    def oneStep(self):
        self.history.append(self.maze)
        pass

    def genMaze(self):
        pass

    def updateDone(self):
        pass

    def undoGen(self):
        self.done = False
        self.maze = self.history.pop()