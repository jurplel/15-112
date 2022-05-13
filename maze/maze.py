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
            self.done = self.updateDone()

    def step(self):
        pass

    def genMaze(self):
        while True:
            self.oneStep()

            if self.done:
                break

        return self.graph

    def updateDone(self):
        pass

    def undoGen(self):
        self.graph = self.history.pop()
        self.done = self.updateDone()
