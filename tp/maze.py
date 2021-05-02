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

# t means target
def drawMazeMap(app, canvas, tx0, ty0, tx1, ty1, color, bgcolor, currentRoom, markerColor):
    width = tx1-tx0
    height = ty1-ty0
    cellHeight = height / app.mazeRows
    cellWidth = width / app.mazeCols
    margin = min(cellWidth/8, cellHeight/8)

    canvas.create_rectangle(tx0, ty0, tx1, ty1, fill=bgcolor, width=0)

    # Copy pasted from mazedebug
    for row in range(app.mazeRows):
        for col in range(app.mazeCols):
            # draw cells
            x0 = tx0+cellWidth*col+margin
            y0 = ty0+cellHeight*row+margin
            x1 = tx0+cellWidth*col+cellWidth-margin
            y1 = ty0+cellHeight*row+cellHeight-margin

            canvas.create_rectangle(x0, y0, x1, y1, width=0, fill=color)

            # draw inbetweeny bits
            for dir in app.maze[row][col].dirs:
                dx, dy = dir.value 
                # m means modified
                mx0, my0, mx1, my1 = x0, y0, x1, y1
                if dx < 0:
                    mx0 += margin*dx
                elif dx > 0:
                    mx1 += margin*dx

                if dy < 0:
                    my0 += margin*dy
                elif dy > 0:
                    my1 += margin*dy

                canvas.create_rectangle(mx0, my0, mx1, my1, width=0, fill=color)

            if currentRoom == (row, col):
                cx = x0+(x1-x0)/2
                cy = y0+(y1-y0)/2
                r = min(cellHeight, cellWidth)/5
                canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=markerColor)

    return margin, margin