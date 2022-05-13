import random

from maze import Maze

class Kruskals(Maze):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.connections = 0

    def step(self):
        while True:
            # get random row, col, and direction to move in
            rRow, rCol = random.randrange(self.rows), random.randrange(self.cols)
            rDir = random.choice([(0, -1), (1, 0), (0, 1), (-1, 0)])

            # get target rows
            tRow, tCol = rRow+rDir[0], rCol+rDir[1]

            # validity check
            valid = self.rows > tRow >= 0 and self.cols > tCol >= 0
            if not valid:
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
            return True

        return False

    def undoGen(self):
        self.connections -= 1
        super().undoGen()