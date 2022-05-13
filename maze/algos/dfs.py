import random, copy

from util import dirs

from maze import Maze

class DFS(Maze):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.backtrackstack = []
        self.backtrackstackhistory = []
        self.visited = set()
        self.visitedHistory = []
        self.connections = 0
    
    def step(self):
        self.backtrackstackhistory.append(copy.deepcopy(self.backtrackstack))
        self.visitedHistory.append(copy.deepcopy(self.visited))

        if len(self.backtrackstack) == 0:
            chosen = random.randrange(self.rows), random.randrange(self.cols)
            self.visited.add(chosen)
            self.backtrackstack.append(chosen)

        found = False
        lastNode = lRow, lCol = self.backtrackstack[-1]
        for drow, dcol in random.sample(dirs, 4):
            currNode = cRow, cCol = lRow+drow, lCol+dcol

            if self.isValid(cRow, cCol) and currNode not in self.visited:
                found = True
                self.visited.add(currNode)
                self.backtrackstack.append(currNode)
                self.graph.addEdge(lastNode, currNode)
                self.connections += 1
                break

        if not found:
            self.backtrackstack.pop()


    def updateDone(self):
        if self.connections == ((self.rows*self.cols)-1):
            self.done = True
        else:
            self.done = False

    def undoGen(self):
        self.connections -= 1
        self.backtrackstack = self.backtrackstackhistory.pop()
        self.visited = self.visitedHistory.pop()
        super().undoGen()
