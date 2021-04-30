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
    app.enemies = []
    app.drops = []
    
    app.maze = None

    ## maze test
    app.mazeRows = app.mazeCols = 2
    app.roomHeight = 50
    app.roomWidth = 100
    app.roomDepth = 20

    meshes = []
    app.maze, enemies = setupMaze(meshes, app.mazeRows, app.mazeCols, app.roomHeight, app.roomWidth, app.roomDepth)
    
    # Move the whole maze over a bit to make room for the player
    # and move it closer to our "ground"
    app.mazeTransform = np.array([-10, -4, -10])
    for i in range(0, len(meshes)):
        meshes[i].translate(app.mazeTransform[0], app.mazeTransform[1], app.mazeTransform[2])

    app.enemies.extend(enemies)
    app.drawables.extend(meshes)

    for enemy in app.enemies:
        enemy.hitCallback = lambda dmg: getHurt(app, dmg)

    # initialize player/cam coordinates
    app.cam = np.array([0, 0, 0, 0], dtype=np.float64)
    app.camDir = np.array([0, 0, 1, 0], dtype=np.float64)
    app.yaw = 0

    app.light = np.array([1, -0.5, 1, 0], dtype=np.float64)
    normVec(app.light)

    # some options
    app.fov = 90
    app.wireframe = False # I recommend trying this option!
    app.drawFps = True
    app.drawCrosshair = True

    app.hudMargin = 15

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

    app.won = None
    app.lost = None

    # player character parameters
    app.health = 100
    app.ammo = 50
    app.weaponDamage = 10
    app.weaponCooldown = 400 # ms
    app.weaponLastShot = time.time()

    app.hurtCooldown = 400
    app.lastHurt = time.time()

def game_sizeChanged(app):
    setNewProjectionMatrix(app)

def setCurrentRoom(app):
    if app.maze == None:
        return

    row = int((app.cam[0] - app.mazeTransform[0]) / app.roomHeight)
    col = int((app.cam[2] - app.mazeTransform[2]) / app.roomWidth)
    app.currentRoom = row, col
    for mesh in app.drawables:
        if app.currentRoom != None and mesh.data.get("mazeinfo", None) != None:  
            meshMazeInfo = mesh.data["mazeinfo"]
            

            rowDiff = abs(meshMazeInfo.row - app.currentRoom[0])
            colDiff = abs(meshMazeInfo.col - app.currentRoom[1])
            
            # isCurrentOrAdjacentRoom = rowDiff <= 1 and colDiff == 0 or colDiff <= 1 and rowDiff == 0

            isCurrentRoom = rowDiff == 0 and colDiff == 0

            mesh.toBeDrawn = isCurrentRoom

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
    for enemy in app.enemies:
        hit = rayIntersectsMeshFirst(enemy.mesh, app.drawables, 
                                app.cam, app.camDir)
        
        # If the enemy isn't blocked by anything (or close to being blocked by our definition)
        # then the enemy got hit!
        if hit:
            drop = enemy.getHit(app.weaponDamage)
            if drop != None:
                drop.pickupCallback = lambda pos: pickupDiamond(app, pos)
                app.drops.append(drop)
                app.drawables.append(drop.mesh)

            print("hit!", enemy.health)
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

def pickupDiamond(app, pos):
    if not app.won:
        app.won = time.time()+3

def getHurt(app, amount):
    if app.health <= 0:
        return

    sinceLastHurt = time.time() - app.lastHurt
    if sinceLastHurt*1000 < app.hurtCooldown:
        return

    app.health -= amount

    if app.health <= 0:
        app.lost = time.time()+3

    app.lastHurt = time.time()

def game_timerFired(app):
    deltaTime = time.time() - app.lastTimerTime

    if app.won and app.won-time.time() < 0:
        app.changeMode(app, "menu")

    if app.lost:
        if app.lost-time.time() < 0:
            app.changeMode(app, "menu")
        return

    processKeys(app, deltaTime)

    for char in app.enemies:
        mazeInfo = char.mesh.data["mazeinfo"]
        charRoom = (mazeInfo.row, mazeInfo.col)
        if charRoom == app.currentRoom:
            char.runAI(app.cam, deltaTime)

    for drop in app.drops:
        mazeInfo = drop.mesh.data["mazeinfo"]
        dropRoom = (mazeInfo.row, mazeInfo.col)
        if dropRoom == app.currentRoom:
            drop.process(app.cam, deltaTime)

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

    # Clip on screen edges in screen space
    morePolys = clipAllPolysOnScreenEdgePlanes(readyPolys, app.height, app.width)
    readyPolys.extend(morePolys)

    # Draw in order with painter's algorithm
    readyPolys.sort(key=paintersAlgorithm)


    # List comprehensions are potentially faster than for loops
    [drawPolygon(app, canvas, x[0], x[1]) for x in readyPolys]

def drawHud(app, canvas):
    canvas.create_text(app.hudMargin, app.height-app.hudMargin, text=app.health, anchor="sw")
    canvas.create_text(app.width-app.hudMargin, app.height-app.hudMargin, text=app.ammo, anchor="se")

    # Current pos HUD
    canvas.create_text(app.hudMargin, app.height-app.hudMargin*3, 
                        text=f"Row {app.currentRoom[0]+1}/{app.mazeRows}, " +
                             f"Col {app.currentRoom[1]+1}/{app.mazeCols}",
                         anchor="sw")


    if app.drawCrosshair:
        r = 2
        canvas.create_rectangle(app.width/2-r, app.height/2-r, app.width/2+r, app.height/2+r,
            fill="white", width=1)

    if app.won or app.lost:
        text = "You win!"
        if app.lost:
            text = "You died."
        
        ry = 20
        rx = 70
        canvas.create_rectangle(app.width/2-rx, app.height/2-ry, app.width/2+rx, app.height/2+ry, fill="white", outline="black")
        canvas.create_text(app.width/2, app.height/2, 
                            text=text, font="Ubuntu 24 italic")

def game_redrawAll(app, canvas):
    if app.drawFps:
        startTime = time.time()

    # Draw all 3D meshes/polygons
    redraw3D(app, canvas)

    drawHud(app, canvas)

    # fps counter
    if app.drawFps:
        denom = time.time()-startTime
        if denom != 0:
            canvas.create_text(15, 15, text=int(1/(time.time()-startTime)), anchor="nw")
