import random

from maze import Maze

class Prims(Maze):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.curr = []

    def step(self):
        if len(self.curr) == 0:
            rRow, rCol = random.randrange(len(self.maze)), random.randrange(len(self.maze[0]))
            rNode = self.maze[rRow][rCol]
            self.curr.append(rNode)
        
        while True:
            rNode = random.choice(self.curr)

