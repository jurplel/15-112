import copy

from graph import Graph

class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.history = []
        self.graph = Graph()
        self.done = False

    def oneStep(self):
        if self.done: 
            return
        else:
            self.history.append(copy.deepcopy(self.graph))
            self.step()
            self.updateDone()

    def step(self):
        pass

    def genMaze(self):
        while True:
            self.oneStep()

            if self.done:
                break

        return self.graph

    def updateDone(self):
        if self.connections == ((self.rows*self.cols)-1):
            self.done = True

    def undoGen(self):
        self.graph = self.history.pop()
        self.updateDone()

    def isValid(self, row, col):
        return self.rows > row >= 0 and self.cols > col >= 0

