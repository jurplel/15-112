from util import make2dList, Node

class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.history = []
        self.maze = make2dList(rows, cols, Node())
        self.done = False

    def oneStep(self):
        if self.done: 
            return
        else:
            self.step()
            self.history.append(self.maze)
            self.done = self.updateDone()

    def step(self):
        pass

    def genMaze(self):
        pass

    def updateDone(self):
        pass

    def undoGen(self):
        self.done = False
        self.maze = self.history.pop()