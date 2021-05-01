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

def drawMazeMap(app, canvas, tx0, ty0, tx1, ty1, color, bgcolor, currentRoom, markerColor):
    width = tx1-tx0
    height = ty1-ty0
    cellHeight = height / app.mazeRows
    cellWidth = width / app.mazeCols    
    marginWidth = cellWidth / 8
    marginHeight = cellHeight / 8

    canvas.create_rectangle(tx0, ty0, tx1, ty1, fill=bgcolor, width=0)

    # Copy pasted from mazedebug
    for row in range(app.mazeRows):
        for col in range(app.mazeCols):
            # draw cells
            x0 = cellWidth*col+marginWidth
            y0 = cellHeight*row+marginHeight
            x1 = cellWidth*col+cellWidth-marginWidth
            y1 = cellHeight*row+cellHeight-marginHeight

            canvas.create_rectangle(tx0+x0, ty0+y0, tx0+x1, ty0+y1, width=0, fill=color)

            # draw inbetweeny bits
            for dir in app.maze[row][col].dirs:
                dx, dy = dir.value 
                # m means modified
                mx0, my0, mx1, my1 = x0, y0, x1, y1
                if dx < 0:
                    mx0 += marginWidth*dx
                elif dx > 0:
                    mx1 += marginWidth*dx

                if dy < 0:
                    my0 += marginHeight*dy
                elif dy > 0:
                    my1 += marginHeight*dy

                canvas.create_rectangle(tx0+mx0, ty0+my0, tx0+mx1, ty0+my1, width=0, fill=color)

            if currentRoom == (row, col):
                r = 15
                canvas.create_oval(tx0+x0+r, ty0+y0+r, tx0+x1-r, ty0+y1-r, fill=markerColor)
