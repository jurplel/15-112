import random, copy

from maze import Maze
from util import dirs

class Prims(Maze):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.visited = set()
        self.visitedHistory = []
        self.frontier = set()
        self.frontierHistory = []

    def addSurroundingToFrontier(self, node: tuple):
        row, col = node
        for drow, dcol in dirs:
            tRow, tCol = row + drow, col + dcol
            if self.isValid(tRow, tCol) and (tRow, tCol) not in self.visited:
                self.frontier.add((tRow, tCol))


    def step(self):
        if len(self.visited) == 0:
            chosen = random.randrange(self.rows), random.randrange(self.cols)
            self.visited.add(chosen)
            self.addSurroundingToFrontier(chosen)
        else:
            fr = frRow, frCol = random.choice(list(self.frontier))
            for drow, dcol in dirs:
                t = tRow, tCol = frRow + drow, frCol + dcol
                if (tRow, tCol) in self.visited:
                    self.graph.addEdge(fr, t)
                    self.frontier.remove(fr)
                    self.addSurroundingToFrontier(fr)
                    self.visited.add(fr)
                    break

        self.visitedHistory.append(copy.deepcopy(self.visited))
        self.frontierHistory.append(copy.deepcopy(self.frontier))

    def updateDone(self):
        if len(self.frontier) == 0:
            self.done = True

    def undoGen(self):
        super().undoGen()
        self.visited = self.visitedHistory.pop()
        self.frontier = self.frontierHistory.pop()