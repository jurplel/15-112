import numpy as np
import math, time

import ply_importer

from dddgame import *

def setNewViewMatrix(app):
    app.viewMatrix = getViewMatrix(app.cam, app.cam + app.camDir)

def setNewProjectionMatrix(app):
    app.projectionMatrix = getProjectionMatrix(app.height, app.width, app.fov)

def startGame(app):
    app.drawables = []

    ## wall test
    # app.drawables.append(createQuadPlane(20, 100))
    # app.drawables[-1].translate(-10, -4, -10)

    ## room test
    # app.drawables.extend(createRoom(50, 100, 20, [Direction.SOUTH, Direction.NORTH]))
    # for i in range(len(app.drawables)-8, len(app.drawables)):
        # app.drawables[i].translate(-10, -4, -10)

    ## maze test
    app.mazeRows = app.mazeCols = 3
    app.roomHeight = 50
    app.roomWidth = 100
    app.roomDepth = 20
    app.maze, meshes = createMaze(3, 3, 50, 100, 20)
    app.drawables.extend(meshes)
    for i in range(0, len(app.drawables)):
        app.drawables[i].translate(-10, -4, -10)

    ## model test
    # app.drawables.append(ply_importer.importPly("res/cube.ply"))
    # app.drawables[-1].translate(4, 0, 4)
    
    app.cam = np.array([0, 0, 0, 0], dtype=np.float64)
    app.camDir = np.array([0, 0, 1, 0], dtype=np.float64)
    app.yaw = 0

    app.light = np.array([0, 0, -1, 0])

    app.fov = 90

    app.wireframe = False
    app.drawFps = True

    setNewProjectionMatrix(app)
    setNewViewMatrix(app)

    targetFps = 144
    app.timerDelay = 1500//targetFps
    app.started = time.time()
    app.lastTime = time.time()
    app.heldKeys = set()

def game_sizeChanged(app):
    setNewProjectionMatrix(app)

def doesCamCollide(app):
    for mesh in app.drawables:
        collides = (mesh.minX-1 <= app.cam[0] <= mesh.maxX+1 and 
                    mesh.minY-1 <= app.cam[1] <= mesh.maxY+1 and 
                    mesh.minZ-1 <= app.cam[2] <= mesh.maxZ+1)
        if collides:
            return True

    return False

def game_keyPressed(app, event):
    key = event.key.lower()
    app.heldKeys.add(key)

def game_keyReleased(app, event):
    key = event.key.lower()
    app.heldKeys.remove(key)

def game_timerFired(app):
    deltaTime = time.time() - app.lastTime
    speed = 15
    speed *= deltaTime
    if app.heldKeys:
        oldCam = copy.deepcopy(app.cam)
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
        
        if doesCamCollide(app):
            app.cam = oldCam

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

## Remains of an attempt at texturing/depth-buffering--ended up with <1fps
# def drawPolygonOnImage(app, polygon, color):
#     # sort by y values, higher on screen/lower value first
#     polygon = polygon[np.argsort(polygon[:,1])]

#     x, y = int(polygon[0][0]), int(polygon[0][1])
#     xa = xb = x

#     if polygon[0][0] == polygon[1][0]:
#         dxa = 0
#     else:
#         dxa = (polygon[0][1]-polygon[1][1])/(polygon[0][0]-polygon[1][0])

#     if polygon[0][0] == polygon[2][0]:
#         dxb = 0
#     else:
#         dxb = (polygon[0][1]-polygon[2][1])/(polygon[0][0]-polygon[2][0])

#     dxa = int(dxa)
#     dxb = int(dxb)

#     if polygon[0][1] != polygon[1][1]:

#         for iy in range(int(polygon[1][1])):
#             xa += dxa
#             xb += dxb

#             for ix in range(xa, xb):
#                 app.canvasImage.put(color, (ix, iy))



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

def game_redrawAll(app, canvas):
    if app.drawFps:
        startTime = time.time()

    # Draw all 3D meshes/polygons
    redraw3D(app, canvas)

    # fps counter
    if app.drawFps:
        canvas.create_text(15, 15, text=int(1/(time.time()-startTime)), anchor="nw")