from dddgame import *
from fpsgameutil import *

import net
import threading
import socket

def startMultiplayer(app):
    initFps(app)
    app.chars = dict()

    # Room for testing
    room = createRoom(100, 100, 20)
    app.drawables.extend(room)

    app.conn = net.connectToServer()
    updateServerInfo(app)

    app.state = dict()
    app.netThread = threading.Thread(target=clientThread, args=(app, gameStateChanged))
    app.netThread.start()

    # Show intro message for this gamemode
    showMsg(app, "Welcome to multiplayer.", 3)

# https://realpython.com/intro-to-python-threading/
def clientThread(app, cb):
    buf = bytearray()
    maybeReadables = [app.conn]
    while True:
        result = net.recvMsg(maybeReadables[0], buf)
        # Disconnect on EOF
        if result == "EOF":
            conn.close()
            print(f"Disconnected from server!")
            return
        elif isinstance(result, dict):
            pass
            app.state = result
            cb(app)


def gameStateChanged(app):
    #idt is id but python already stole id >:(
    idtList = []
    for key in app.state:
        found = False
        idt = int(key[0])
        if not idt in idtList:
            idtList.append(idt)

    for charIdt, char in app.chars.items():
        if not charIdt in idtList:
            app.drawables.remove(charIdt.mesh)
            idtList.remove(charIdt)

        posKey = str(charIdt) + "pos"
        dirKey = str(charIdt) + "dir"
        char.mesh.moveTo(app.state[posKey][0], app.state[posKey][1], app.state[posKey][2])
        char.facePoint(app.state[posKey]+app.state[dirKey])


    for idt in idtList:
        if app.chars.get(idt, None) == None:
            newChar = Character()
            app.chars[idt] = newChar
            app.drawables.append(newChar.mesh)


def multiplayer_appStopped(app):
    if hasattr(app, "conn") and isinstance(app.conn, socket.socket):
        print("Killing remaining connection...")
        app.conn.close() # Don't know why this causes exception but oh well

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

def updateServerInfo(app):
    info = {"pos": app.cam, "dir": app.camDir}
    net.sendInfo(info, app.conn)

def multiplayer_timerFired(app):
    deltaTime = time.time() - app.lastTimerTime
    fpsGameProcess(app, deltaTime)

    if app.msgMovementAllowed:
        moved = processKeys(app, deltaTime)
        if moved: 
            updateServerInfo(app)

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
