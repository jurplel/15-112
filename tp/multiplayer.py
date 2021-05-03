import dddgame
from fpsgameutil import *

import net

def startMultiplayer(app):
    initFps(app)

    # Room for testing
    room = dddgame.createRoom(100, 100, 20)
    app.drawables.extend(room)

    app.conn = net.connectToServer()
    info = {"pos": app.cam, "dir": app.camDir}
    net.sendInfo(info, app.conn)

    # Show intro message for this gamemode
    showMsg(app, "Welcome to multiplayer.", 3)

def multiplayer_sizeChanged(app):
    fpsSizeChanged(app)

def multiplayer_keyPressed(app, event):
    key = event.key.lower()
    app.heldKeys.add(key)

def multiplayer_keyReleased(app, event):
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

def multiplayer_timerFired(app):
    deltaTime = time.time() - app.lastTimerTime
    fpsGameProcess(app, deltaTime)

    if app.msgMovementAllowed:
        _moved = processKeys(app, deltaTime)

    app.lastTimerTime = time.time()


def multiplayer_redrawAll(app, canvas):
    if app.drawFps:
        startTime = time.time()

    # Draw all 3D meshes/polygons
    redraw3D(app, canvas)

    drawMsg(app, canvas)

    drawWeaponSprite(app, canvas)

    # fps counter
    if app.drawFps:
        denom = time.time()-startTime
        if denom != 0:
            canvas.create_text(15, 15, text=int(1/(time.time()-startTime)), anchor="nw", fill="gray50")
