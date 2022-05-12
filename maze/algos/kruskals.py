import random

from maze import Maze
from util import Node, Direction

class Kruskals(Maze):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.connections = 0


    def genMaze(self):
        while True:
            self.oneStep()

            if self.done:
                break

        return self.maze

    def step(self):
        while True:
            # get random row, col, and direction to move in
            rRow, rCol = random.randrange(len(self.maze)), random.randrange(len(self.maze[0]))
            rDir = random.choice(list(Direction))

            # get target rows
            tRow, tCol = rRow+rDir.value[1], rCol+rDir.value[0]

            # validity check
            valid = self.rows > tRow >= 0 and self.cols > tCol >= 0
            if not valid:
                continue


            rVal = self.maze[rRow][rCol]
            tVal = self.maze[tRow][tCol]
            # check if the chosen and target cell are connected
            # if they aren't merge the "sets"
            if not tVal.connected(rVal):
                tVal.connect(rVal)
                rVal.dirs.append(rDir)
                tVal.dirs.append(~rDir)
                self.connections += 1
                break

    def updateDone(self):
        if self.connections == ((self.rows*self.cols)-1):
            self.done = True
            return True

        return False

    def undoGen(self):
        super().undoGen()
        self.connections -= 1