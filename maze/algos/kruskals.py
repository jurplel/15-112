import random

from util import dirs

from maze import Maze

class Kruskals(Maze):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.connections = 0

    def step(self):
        while True:
            # get random row, col, and direction to move in
            rRow, rCol = random.randrange(self.rows), random.randrange(self.cols)
            rDir = random.choice(dirs)

            # get target rows
            tRow, tCol = rRow+rDir[0], rCol+rDir[1]

            # validity check
            if not self.isValid(tRow, tCol):
                continue


            rVal = (rRow, rCol)
            tVal = (tRow, tCol)
            # check if the chosen and target cell are connected
            # if they aren't merge the "sets"
            if not self.graph.sharedRoot(tVal, rVal):
                self.graph.addEdge(tVal, rVal)
                self.graph.makeParent(tVal, rVal)
                self.connections += 1
                break

    def updateDone(self):
        if self.connections == ((self.rows*self.cols)-1):
            self.done = True

    def undoGen(self):
        self.connections -= 1
        super().undoGen()