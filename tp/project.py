# Some sources
# https://www.scratchapixel.com/
# https://www.youtube.com/watch?v=ih20l3pJoeU (No code copied, just used to push concepts along!)
# https://en.wikipedia.org/wiki/Rotation_matrix
# https://sites.google.com/site/3dprogramminginpython/ (Did not look at any code!!!)
# http://graphics.cs.cmu.edu/nsp/course/15-462/Spring04/slides/06-viewing.pdf

from dataclasses import dataclass

from cmu_112_graphics import *

import numpy as np
import math, time

import ply_importer

from threedee import *

def setNewViewMatrix(app):
    app.viewMatrix = getViewMatrix(app.cam, app.cam + app.camDir)

def setNewProjectionMatrix(app):
    app.projectionMatrix = getProjectionMatrix(app.height, app.width, app.fov)

def appStarted(app):
    app.drawables = []
    app.drawables.append(ply_importer.importPly("cube.ply"))
    # app.drawables.append(createQuadPlane(10, 100))
    
    app.cam = np.array([0, 0, 0, 0], dtype=np.float64)
    app.camDir = np.array([0, 0, 1, 0], dtype=np.float64)
    app.yaw = 0

    app.light = np.array([0, 0, -1, 0])

    app.fov = 90

    app.wireframe = False

    setNewProjectionMatrix(app)
    setNewViewMatrix(app)

    targetFps = 144
    app.timerDelay = 1500//targetFps
    app.started = time.time()
    app.lastTime = time.time()
    app.heldKeys = set()

def sizeChanged(app):
    setNewProjectionMatrix(app)

def keyPressed(app, event):
    key = event.key.lower()
    app.heldKeys.add(key)

def keyReleased(app, event):
    key = event.key.lower()
    app.heldKeys.remove(key)

def timerFired(app):
    deltaTime = time.time() - app.lastTime
    speed = deltaTime * 10
    if app.heldKeys:
        # vertex additions
        if "w" in app.heldKeys:
            app.cam += app.camDir * speed
        elif "s" in app.heldKeys:
            app.cam -= app.camDir * speed

        sidewaysRotationMatrix = getRotationMatrix(0, 90, 0)
        sidewaysCamDir = sidewaysRotationMatrix @ app.camDir

        if "a" in app.heldKeys:
            app.cam -= sidewaysCamDir * speed
        elif "d" in app.heldKeys:
            app.cam += sidewaysCamDir * speed
        
        angleStep = 15
        angleStep *= speed

        # rotations        
        if "left" in app.heldKeys:
            app.yaw += angleStep
        elif "right" in app.heldKeys:
            app.yaw -= angleStep

        app.camDir = np.array([0, 0, 1, 0]) @ getYRotationMatrix(app.yaw)
        setNewViewMatrix(app)

    app.lastTime = time.time()


def drawPolygon(app, canvas, polygon, color):
    v0 = polygon[0]
    v1 = polygon[1]
    v2 = polygon[2]

    outlineColor = "black" if app.wireframe else color
    canvas.create_polygon(v0[0], v0[1], v1[0], v1[1], v2[0], v2[1], 
                        outline=outlineColor, fill=color)


def redraw3D(app, canvas):
    readyPolys = []
    for mesh in app.drawables:
        readyPolys.extend(mesh.process(app.cam, app.light,
                                       app.height, app.width,
                                       app.projectionMatrix, app.viewMatrix))


    # Draw in order with painter's algorithm
    readyPolys.sort(key=paintersAlgorithm)

    # List comprehensions are potentially faster than for loops
    [drawPolygon(app, canvas, x[0], x[1]) for x in readyPolys]


def redrawAll(app, canvas):
    startTime = time.time()

    # Draw all 3D meshes/polygons
    redraw3D(app, canvas)

    # fps counter
    canvas.create_text(15, 15, text=int(1/(time.time()-startTime)), anchor="nw")

def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
