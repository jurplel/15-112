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
    app.characters = []
    
    ## maze test
    app.mazeRows = app.mazeCols = 3
    app.roomHeight = 50
    app.roomWidth = 100
    app.roomDepth = 20
    app.maze, meshes = createMaze(app.mazeRows, app.mazeCols, app.roomHeight, app.roomWidth, app.roomDepth)
    app.mazeTransform = np.array([-10, -4, -10])
    for i in range(0, len(meshes)):
        meshes[i].translate(app.mazeTransform[0], app.mazeTransform[1], app.mazeTransform[2])
    
    enemies = populateMazeWithEnemies(app.maze, meshes, app.roomHeight, app.roomWidth)
    app.characters.extend(enemies)

    app.drawables.extend(meshes)

    ## character test
    # app.characters.append(Character(ply_importer.importPly("res/char.ply")))
    # app.drawables.append(app.characters[-1].mesh)
    # app.drawables[-1].translate(4, -3, 4)

    # initialize player/cam coordinates
    app.cam = np.array([0, 0, 0, 0], dtype=np.float64)
    app.camDir = np.array([0, 0, 1, 0], dtype=np.float64)
    app.yaw = 0

    app.light = np.array([0, 0, -1, 0])

    # some options
    app.fov = 90
    app.wireframe = False
    app.drawFps = True

    app.timerDelay = 1

    app.movementSpeed = 15

    # initialize matrices
    setNewProjectionMatrix(app)
    setNewViewMatrix(app)
    
    # initialize game logic

    app.started = time.time()
    app.lastTimerTime = time.time()

    app.heldKeys = set()

    setCurrentRoom(app)

    # player character parameters
    app.health = 100
    app.ammo = 50
    app.weaponDamage = 10
    app.weaponCooldown = 400 # ms
    app.weaponLastShot = time.time()
    app.weaponRange = 50

def game_sizeChanged(app):
    setNewProjectionMatrix(app)

def doesCamCollide(app):
    # -1 and +1 is basically the camera/player's imaginary hitbox
    for mesh in app.drawables:
        collides = (mesh.minX-1 <= app.cam[0] <= mesh.maxX+1 and 
                    mesh.minY-1 <= app.cam[1] <= mesh.maxY+1 and 
                    mesh.minZ-1 <= app.cam[2] <= mesh.maxZ+1)
        if collides:
            return True

    return False

def setCurrentRoom(app):
    row = int((app.cam[0] - app.mazeTransform[0]) / app.roomHeight)
    col = int((app.cam[2] - app.mazeTransform[2]) / app.roomWidth)
    app.currentRoom = row, col
    for mesh in app.drawables:
        if app.currentRoom != None and mesh.data.get("mazeinfo", None) != None:  
            meshMazeInfo = mesh.data["mazeinfo"]
            

            rowDiff = abs(meshMazeInfo.row - app.currentRoom[0])
            colDiff = abs(meshMazeInfo.col - app.currentRoom[1])
            
            isCurrentOrAdjacentRoom = rowDiff <= 1 and colDiff == 0 or colDiff <= 1 and rowDiff == 0

            mesh.visible = isCurrentOrAdjacentRoom

def game_keyPressed(app, event):
    key = event.key.lower()
    app.heldKeys.add(key)

def game_keyReleased(app, event):
    key = event.key.lower()
    app.heldKeys.remove(key)

# drz/drx is delta relative z/x
def relativeCamMove(app, drz, drx):
    oldCam = copy.deepcopy(app.cam)
    app.cam += app.camDir * drz

    sidewaysCamDir = app.camDir @ getRotationMatrix(0, 90, 0)

    app.cam += sidewaysCamDir * drx

    for mesh in app.drawables:
        if pointCollision(mesh, app.cam, 1):
            app.cam = oldCam
            return

    setCurrentRoom(app)

    
def recalculateCamDir(app):
    app.camDir = np.array([0, 0, 1, 0]) @ getYRotationMatrix(app.yaw)

    setNewViewMatrix(app)

def fireGun(app):
    sinceLastFired = time.time() - app.weaponLastShot
    if sinceLastFired*1000 < app.weaponCooldown:
        return

    app.weaponLastShot = time.time()
    for character in app.characters:
        hit = rayIntersectsMeshFirst(character.mesh, app.drawables, 
                                app.cam, app.camDir, app.weaponRange)
        
        # If the character isn't blocked by anything (or close to being blocked by our definition)
        # then the character got hit!
        if hit:
            character.getHit(app.weaponDamage)
            print("hit", character.health)
            break
        


def processKeys(app, deltaTime):
    speed = app.movementSpeed*deltaTime
    if app.heldKeys:
        # delta relative x/z
        drx = 0
        drz = 0
        # camera movements
        if "w" in app.heldKeys:
            drz += speed
        elif "s" in app.heldKeys:
            drz -= speed

        if "a" in app.heldKeys:
            drx += speed
        elif "d" in app.heldKeys:
            drx -= speed

        relativeCamMove(app, drz, drx)

        # weird but i'm leaving this i guess
        angleStep = app.movementSpeed*speed

        # rotations        
        if "left" in app.heldKeys:
            app.yaw += angleStep
        elif "right" in app.heldKeys:
            app.yaw -= angleStep


        recalculateCamDir(app)

        if "space" in app.heldKeys:
            fireGun(app)


def game_timerFired(app):
    deltaTime = time.time() - app.lastTimerTime
    processKeys(app, deltaTime)
    app.lastTimerTime = time.time()


## Remains of an attempt at starting texturing/depth-buffering--ended up with <1fps so I gave up
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
        denom = time.time()-startTime
        if denom != 0:
            canvas.create_text(15, 15, text=int(1/(time.time()-startTime)), anchor="nw")

    canvas.create_text(15, app.height-15, text=app.health, anchor="sw")
    canvas.create_text(app.width-15, app.height-15, text=app.ammo, anchor="se")