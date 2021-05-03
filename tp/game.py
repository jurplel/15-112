from cmu_112_graphics import *

import numpy as np
import math, time

import ply_importer

from dddgame import *
from maze import drawMazeMap

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

def setCurrentRoom(app):
    if app.maze == None:
        return

    row = int(app.cam[0] / app.roomHeight)
    col = int(app.cam[2] / app.roomWidth)
    newRoom = True if (row, col) != app.currentRoom else False

    app.currentRoom = row, col

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


    if newRoom:
        app.doorCloseTimer = time.time()+1


def game_keyPressed(app, event):
    key = event.key.lower()
    app.heldKeys.add(key)

def game_keyReleased(app, event):
    key = event.key.lower()
    if key in app.heldKeys:
        app.heldKeys.remove(key)

def fireWeapon(app, weapon):
    sinceLastFired = time.time() - weapon.lastShot
    if sinceLastFired*1000 < weapon.cooldown:
        return

    weapon.lastShot = time.time()
    if weapon.hasSprites:
        weapon.spriteState = 1
    
    weapon.playSound()
    for char in app.chars:
        hit = rayIntersectsMeshFirst(char.mesh, app.drawables, 
                                app.cam, app.camDir)
        
        # If the enemy isn't blocked by anything (or close to being blocked by our definition)
        # then the enemy got hit!
        if hit:
            # check if its in the current room too!
            mazeInfo = char.mesh.data["mazeinfo"]
            if not (mazeInfo.row, mazeInfo.col) == app.currentRoom:
                return

            drop = char.getHit(weapon.damage)
            if drop != None:
                if drop.mesh.data["pickup"] == "win":
                    drop.pickupCallback = lambda pos: pickupDiamond(app, pos)
                elif drop.mesh.data["pickup"] == "health":
                    drop.pickupCallback = lambda pos: pickupHealth(app)
                app.drops.append(drop)
                app.drawables.append(drop.mesh)

            # Set damage indicator variables
            app.lastHitName = char.name
            app.lastHitHealth = char.health
            app.lastHitMaxHealth = char.maxHealth
            app.lastHitTime = time.time()+3
            break


def pickupDiamond(app, pos):
    showMsg(app, "You win!", 3, True, True)

def pickupHealth(app):
    app.health += 50
    if app.health > 100:
        app.health = 100

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

def game_timerFired(app):
    deltaTime = time.time() - app.lastTimerTime
    fpsGameProcess(app, deltaTime)


    if app.doorCloseTimer != None and app.doorCloseTimer-time.time() < 0:
        for door in app.doorsToClose:
            door.visible = True

    if app.msgMovementAllowed:
        moved = processKeys(app, deltaTime)
        if moved:
            setCurrentRoom(app)

    for char in app.chars:
        if not isinstance(char, Enemy):
            continue
        mazeInfo = char.mesh.data["mazeinfo"]
        charRoom = (mazeInfo.row, mazeInfo.col)
        if charRoom == app.currentRoom:
            char.runAI(app.cam, deltaTime)

    for drop in app.drops:
        if drop.mesh.toBeDrawn == False:
            continue
        mazeInfo = drop.mesh.data["mazeinfo"]
        dropRoom = (mazeInfo.row, mazeInfo.col)
        if dropRoom == app.currentRoom:
            drop.process(app.cam, deltaTime)

    app.lastTimerTime = time.time()

# stipple from https://stackoverflow.com/questions/15468327/how-can-i-vary-a-shapes-alpha-with-tkinter
def drawHud(app, canvas):
    # Health and minimap HUD
    healthX = app.hudMargin
    healthY = app.height-app.hudMargin
    healthW = 200
    healthH = 20

    healthColor = "lawn green" if app.health > 25 else "tomato2" # Why do i always choose the weird colors

    marginWidth, marginHeight = drawMazeMap(app, canvas, healthX, healthY-healthW, healthX+healthW, 
                                            healthY-healthH, "gray60", "gray25", app.currentRoom, healthColor)

    canvas.create_rectangle(healthX, healthY-healthH, healthX+healthW*(app.health/100), healthY, width=0, fill=healthColor)
    canvas.create_rectangle(healthX+marginWidth/2, healthY-healthH, healthX+healthW-marginWidth/2, healthY, width=marginWidth, outline="gray25")

    # Damage indicator
    if app.lastHitName != None:
        indicatorX = app.width-app.hudMargin-healthW
        indicatorY = app.hudMargin
        enemyHealthColor = "lawn green" if app.lastHitHealth > app.lastHitMaxHealth*0.25 else "tomato2"
        canvas.create_rectangle(indicatorX, indicatorY, indicatorX+healthW, indicatorY+healthH*3, fill= "gray60", width=marginWidth, outline="gray25")

        canvas.create_text(indicatorX+marginWidth, indicatorY+marginWidth, 
                            text=f"{app.lastHitName}\n", anchor="nw", font="Ubuntu 14 italic", fill="black")

        canvas.create_rectangle(indicatorX, indicatorY+healthH*2, indicatorX+healthW*(app.lastHitHealth)/app.lastHitMaxHealth, 
                                indicatorY+healthH*3, width=0, fill=enemyHealthColor, outline="gray25")
                                
        canvas.create_rectangle(indicatorX, indicatorY+healthH*2, indicatorX+healthW, indicatorY+healthH*3, outline="gray25", width=marginWidth)


    if app.drawCrosshair:
        r = 2
        canvas.create_rectangle(app.width/2-r, app.height/2-r, app.width/2+r, app.height/2+r,
            fill="white", width=1, outline="black")

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
