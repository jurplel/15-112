# Literally just made to test the maze algorithm

from cmu_112_graphics import *

from algos.kruskals import Kruskals
from algos.prims import Prims
from algos.ellers import Ellers
from algos.dfs import DFS

def setCellSizes(app):
    app.cellWidth = app.width / app.cols
    app.cellHeight = app.height / app.rows
    app.marginWidth = app.cellWidth / 4
    app.marginHeight = app.cellHeight / 4

def appStarted(app):
    app.rows = 16
    app.cols = 16
    app.maze = DFS(app.rows, app.cols)
    app.paused = False
    app.timerDelay = 16
    setCellSizes(app)

def keyPressed(app, event):
    key = event.key.lower()
    if key == "space":
        app.paused = not app.paused
    elif key == "left":
        app.maze.undoGen()
    elif key == "right":
        app.maze.oneStep()
    elif key == "f":
        app.maze.genMaze()
    elif key == "r":
        app.maze = DFS(app.rows, app.cols)

def timerFired(app):
    if app.paused: return

    app.maze.oneStep()

def sizeChanged(app):
    setCellSizes(app)

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, width=0, fill="gray25")
    for row in range(app.rows):
        for col in range(app.cols):
            # draw cells
            x0 = app.cellWidth*col+app.marginWidth
            y0 = app.cellHeight*row+app.marginHeight
            x1 = app.cellWidth*col+app.cellWidth-app.marginWidth
            y1 = app.cellHeight*row+app.cellHeight-app.marginHeight

            canvas.create_rectangle(x0, y0, x1, y1, width=0, fill="bisque2")

            # draw inbetweeny bits
            for cRow, cCol in app.maze.graph.getEdges((row, col)):
                drow, dcol = cRow-row, cCol-col
                # m means modified i guess idk this doesn't really matter
                mx0, my0, mx1, my1 = x0, y0, x1, y1
                if drow < 0:
                    my0 += app.marginWidth*drow
                elif drow > 0:
                    my1 += app.marginWidth*drow

                if dcol < 0:
                    mx0 += app.marginHeight*dcol
                elif dcol > 0:
                    mx1 += app.marginHeight*dcol

                canvas.create_rectangle(mx0, my0, mx1, my1, width=0, fill="bisque2")


def main():
    width = 768
    height = 768
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
