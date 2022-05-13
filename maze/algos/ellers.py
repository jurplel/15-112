import random

from maze import Maze

class Ellers(Maze):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.currRow = 0

    def step(self):
        # if last row, connect all adjacent, disjoint
        if self.currRow == self.rows - 1:
            for col in range(self.cols - 1):
                nodeA, nodeB = (self.currRow, col), (self.currRow, col + 1)
                if self.graph.root(nodeA) == self.graph.root(nodeB):
                    continue

                self.graph.addEdge(nodeA, nodeB)
                self.graph.makeParent(nodeB, nodeA)

        # otherwise,
        else:
            # connect random adjacent cells in a row
            for col in range(self.cols - 1):
                connect = random.choice([True, False])
                if connect:
                    nodeA, nodeB = (self.currRow, col), (self.currRow, col + 1)
                    if self.graph.root(nodeA) == self.graph.root(nodeB):
                        continue

                    self.graph.addEdge(nodeA, nodeB)
                    self.graph.makeParent(nodeB, nodeA)

            # make random connections to next row
            roots = set()
            for col in range(self.cols):
                connect = random.choice([True, False])
                if connect:
                    nodeA, nodeB = (self.currRow, col), (self.currRow + 1, col)
                    self.graph.addEdge(nodeA, nodeB)
                    self.graph.makeParent(nodeB, nodeA)
                    root = self.graph.root(nodeA)
                    roots.add(root)

            # ensure all sets are connected at least once
            for col in range(self.cols):
                nodeA, nodeB = (self.currRow, col), (self.currRow + 1, col)
                if self.graph.root(nodeA) not in roots:
                    self.graph.addEdge(nodeA, nodeB)
                    self.graph.makeParent(nodeB, nodeA)

        self.currRow += 1

    def updateDone(self):
        if self.currRow == self.rows:
            self.done = True
        else:
            self.done = False


    def undoGen(self):
        self.currRow -= 1
        super().undoGen()
