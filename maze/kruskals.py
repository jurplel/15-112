import random

from maze import Maze

from util import Direction

class Node:
    def __init__(self, id):
        self.id = id
        self.partners = []
        self.dirs = []

    def __repr__(self):
        return f"Node({self.id}, {self.dirs})"

    def convert(self, newId):
        if self.id == newId:
            return

        self.id = newId
        for partner in self.partners:
            partner.convert(newId)


class Kruskals(Maze):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)

        id = 0
        for row in range(rows):
            for col in range(cols):
                self.maze[row][col] = Node(id)
                id += 1


    def genMaze(self):
        while True:
            self.oneStep()

            done = self.updateDone()

            if done:
                break

        return self.maze



    def oneStep(self):
        super().oneStep()

        while True:
            # get random row, col, and direction to move in
            rRow, rCol = random.randrange(len(self.maze)), random.randrange(len(self.maze[0]))
            rDir = random.choice(list(Direction))

            # get target rows
            tRow, tCol = rRow+rDir.value[1], rCol+rDir.value[0]

            # validity check
            valid = self.rows > tRow >= 0 and self.cols > tCol >= 0
            if valid:
                break

        # check if the chosen and target cell are different ids
        # if they aren't merge the "sets"
        rVal = self.maze[rRow][rCol]
        tVal = self.maze[tRow][tCol]
        if tVal.id != rVal.id:
            rVal.partners.append(tVal)
            rVal.dirs.append(rDir)
            tVal.partners.append(rVal)
            tVal.dirs.append(~rDir)
            tVal.convert(rVal.id)



    def updateDone(self):
        # if we ever have only one id in the whole graph, quit
        uniques = set()
        for row in self.maze:
            for v in row:
                uniques.add(v.id)

        if len(uniques) == 1:
            self.done = True
            return True

        return False
