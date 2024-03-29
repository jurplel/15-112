# The tkinter/cmu_112_graphics side of the singleplayer game mode. 
# Most of the specific logic here is actually just for door closing as nearly all of the singleplayer stuff has been exported to fpsgameutil.

from cmu_112_graphics import *

import numpy as np
import math, time

import ply_importer

from dddgame import *

from fpsgameutil import *

def startGame(app):
    initFps(app)
    
    # Initialize maze
    app.mazeRows = random.randint(4, 8)
    app.mazeCols = random.randint(4, 8)
    app.roomHeight = 50
    app.roomWidth = 100
    app.roomDepth = 20

    meshes = []
    app.maze, enemies, drops = setupMaze(meshes, app.mazeRows, app.mazeCols, app.roomHeight, app.roomWidth, app.roomDepth)
    
    # Move the whole maze over a bit to make room for the player
    # and move it closer to our "ground"
    app.chars.extend(enemies)
    app.drawables.extend(meshes)
    
    app.drops.extend(drops)
    for drop in drops:
        drop.pickupCallback = lambda pos: pickupWeapon(app)

    for char in app.chars:
        if isinstance(char, Enemy):
            char.hitCallback = lambda dmg: getHurt(app, dmg)

    # Game logic
    app.doorsToClose = []
    app.doorCloseTimer = None
    app.currentRoom = (0, 0)
    setCurrentRoom(app)

    # Show intro message for this gamemode
    showMsg(app, "Your mission:\n" +
                 f"Elliminate the boss at the bottom right corner\n" +
                 "of the maze and recover the diamond.", 5)

    pygame.mixer.music.load("res/d_e2m1.ogg")
    pygame.mixer.music.play(-1)

def game_sizeChanged(app):
    fpsSizeChanged(app)

def livingEnemiesInThisRoom(app):
    for char in app.chars:
        if char.dead:
            continue

        if not "mazeinfo" in char.mesh.data:
            continue

        row = char.mesh.data["mazeinfo"].row
        col = char.mesh.data["mazeinfo"].col

        if (row, col) == app.currentRoom:
            return True

    return False

def game_keyPressed(app, event):
    key = event.key.lower()
    if key == "h":
        app.cam = copy.deepcopy(app.defaultCam)
        setCurrentRoom(app)
    elif key == "m":
        app.health = 100

    if key == "escape":
        app.changeMode(app, "menu")

    app.heldKeys.add(key)

def game_keyReleased(app, event):
    key = event.key.lower()
    if key in app.heldKeys:
        app.heldKeys.remove(key)

def processKeys(app, deltaTime):
    speed = app.movementSpeed*deltaTime
    turnSpeed = app.turnSpeed*speed
    if app.heldKeys:
        app.noclip = "n" in app.heldKeys

        if "tab" in app.heldKeys:
            speed *= 2
            turnSpeed *= 1.5
        # delta relative x/z
        drx = 0
        drz = 0
        # camera movements
        if "w" in app.heldKeys:
            drz += speed
        elif "s" in app.heldKeys:
            if "tab" in app.heldKeys:
                speed *= 0.5
            drz -= speed

        if "a" in app.heldKeys:
            drx += speed
        elif "d" in app.heldKeys:
            drx -= speed

        moved = relativeCamMove(app, drz, drx)


        # rotations        
        if "left" in app.heldKeys:
            app.yaw += turnSpeed
        elif "right" in app.heldKeys:
            app.yaw -= turnSpeed


        recalculateCamDir(app)

        if "space" in app.heldKeys:
            fireWeapon(app, app.weapons[app.currentWeapon])

        if "r" in app.heldKeys:
                    switchWeapon(app)

        return moved

def updateDoors(app):
    if app.maze == None:
        return

    livingEnemies = livingEnemiesInThisRoom(app)
    
    app.doorsToClose = []

    for mesh in app.drawables:
        if app.currentRoom != None and mesh.data.get("mazeinfo", None) != None:
            meshMazeInfo = mesh.data["mazeinfo"]

            rowDiff = abs(meshMazeInfo.row - app.currentRoom[0])
            colDiff = abs(meshMazeInfo.col - app.currentRoom[1])
            
            isCurrentRoom = rowDiff == 0 and colDiff == 0

            mesh.toBeDrawn = isCurrentRoom

            if "door" in mesh.data and mesh.data["door"] == True:
                if isCurrentRoom and livingEnemies:
                    app.doorsToClose.append(mesh)
                else:
                    mesh.visible = False


    if app.roomJustChanged:
        app.doorCloseTimer = time.time()+1

def processEnemies(app, deltaTime):
    for char in app.chars:
        if not isinstance(char, Enemy):
            continue
        mazeInfo = char.mesh.data["mazeinfo"]
        charRoom = (mazeInfo.row, mazeInfo.col)
        if charRoom == app.currentRoom:
            char.runAI(app.cam, deltaTime)

def game_timerFired(app):
    deltaTime = time.time() - app.lastTimerTime
    fpsGameProcess(app, deltaTime)
    processEnemies(app, deltaTime)

    if app.doorCloseTimer != None and app.doorCloseTimer-time.time() < 0:
        for door in app.doorsToClose:
            door.visible = True

    if app.msgMovementAllowed:
        moved = processKeys(app, deltaTime)
        if moved:
            updateDoors(app)

    app.lastTimerTime = time.time()

def game_redrawAll(app, canvas):
    if app.drawFps:
        startTime = time.time()

    # Draw all 3D meshes/polygons
    redraw3D(app, canvas)

    drawHud(app, canvas)

    drawMsg(app, canvas)

    drawWeaponSprite(app, canvas)

    # fps counter
    if app.drawFps:
        denom = time.time()-startTime
        if denom != 0:
            canvas.create_text(15, 15, text=int(1/(time.time()-startTime)), anchor="nw", fill="gray50")
