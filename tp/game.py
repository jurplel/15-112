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
    app.maze, enemies = setupMaze(meshes, app.mazeRows, app.mazeCols, app.roomHeight, app.roomWidth, app.roomDepth)
    
    # Move the whole maze over a bit to make room for the player
    # and move it closer to our "ground"
    app.chars.extend(enemies)
    app.drawables.extend(meshes)

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

    pygame.mixer.music.load("res/d_e2m1.mp3")
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
    if key == "escape":
        app.changeMode(app, "menu")

    app.heldKeys.add(key)

def game_keyReleased(app, event):
    key = event.key.lower()
    if key in app.heldKeys:
        app.heldKeys.remove(key)

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

        moved = relativeCamMove(app, drz, drx)

        # weird but i'm leaving this i guess
        angleStep = app.movementSpeed*speed

        # rotations        
        if "left" in app.heldKeys:
            app.yaw += angleStep
        elif "right" in app.heldKeys:
            app.yaw -= angleStep


        recalculateCamDir(app)

        if "space" in app.heldKeys:
            fireWeapon(app, app.weapons[0])

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
