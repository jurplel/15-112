# Source: http://weblog.jamisbuck.org/2011/1/3/maze-generation-kruskal-s-algorithm

import random

from util import *

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

# http://weblog.jamisbuck.org/2011/1/3/maze-generation-kruskal-s-algorithm#
def genMaze(rows, cols):
    graph = make2dList(rows, cols, None)
    id = 0
    for row in range(rows):
        for col in range(cols):
            graph[row][col] = Node(id)
            id += 1

    # r = random, t = target
    while True:
        # get random row, col, and direction to move in
        rRow, rCol = random.randrange(len(graph)), random.randrange(len(graph[0]))
        rDir = random.choice(list(Direction))

        # get target rows
        tRow, tCol = rRow+rDir.value[1], rCol+rDir.value[0]

        # validity check
        valid = rows > tRow >= 0 and cols > tCol >= 0
        if not valid:
            continue

        # check if the chosen and target cell are different ids
        # if they aren't merge the "sets"
        rVal = graph[rRow][rCol]
        tVal = graph[tRow][tCol]
        if tVal.id != rVal.id:
            rVal.partners.append(tVal)
            rVal.dirs.append(rDir)
            tVal.partners.append(rVal)
            tVal.dirs.append(~rDir)
            tVal.convert(rVal.id)

        # if we ever have only one id in the whole graph, quit
        uniques = set()
        for row in graph:
            for v in row:
                uniques.add(v.id)

        if len(uniques) == 1:
            break

    return graph

def mazeTo3DEnvironment():
    pass