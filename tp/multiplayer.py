from dddgame import *
from fpsgameutil import *

import net
import threading
import socket

def startMultiplayer(app):
    initFps(app)

    # Room for testing
    room = createRoom(100, 100, 20)
    app.drawables.extend(room)

    app.conn = net.connectToServer()

    app.state = dict()
    app.stateChanged = False
    app.netThread = threading.Thread(target=clientThread, args=(app,))
    app.netThread.start()

    updateServerInfo(app)


    # Show intro message for this gamemode
    showMsg(app, "Welcome to multiplayer.", 3)

# https://realpython.com/intro-to-python-threading/
def clientThread(app):
    buf = bytearray()
    maybeReadables = [app.conn]
    while True:
        result = net.recvMsg(maybeReadables[0], buf)
        # Disconnect on EOF
        if result == "EOF":
            app.conn.close()
            print(f"Disconnected from server!")
            return
        elif isinstance(result, dict):
            app.state = result
            app.stateChanged = True


def gameStateChanged(app):
    print(app.state)
    app.stateChanged = False
    #idt is id but python already stole id >:(
    # make list of ids from state
    stateIdts = []
    for key in app.state:
        found = False
        if "pos" in key:
            idt = int(key[0])
            if not idt in stateIdts:
                stateIdts.append(idt)

    for key in app.state:
        for idt in stateIdts:
            if str(idt) not in key and "health" in key:
                app.health = app.state[key]

    # Add any new characters
    for idt in stateIdts:
        found = False
        for char in app.chars:
            mpid = char.mesh.data.get("mpid", None)
            if mpid != None and mpid == idt:
                found = True

        if not found:
            newChar = Character()
            newChar.mesh.data["mpid"] = idt
            app.chars.append(newChar)
            app.drawables.append(newChar.mesh)

    # Delete any old characters and set the positions of existing ones
    toRemove = []
    for char in app.chars:
        charIdt = char.mesh.data["mpid"]
        if not charIdt in stateIdts:
            app.drawables.remove(char.mesh)
            toRemove.append(char)
            continue


        posKey = str(charIdt) + "pos"
        dirKey = str(charIdt) + "dir"
        char.mesh.moveTo(app.state[posKey][0], app.state[posKey][1], app.state[posKey][2])
        char.facePoint(app.state[posKey]+app.state[dirKey])
        char.health = app.state[str(charIdt) + "health"]

    # This is still the deletion bit obviously
    for char in toRemove:
        app.chars.remove(char)
        


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
            hit = fireWeapon(app, app.weapons[0])
            forwardHitToServer(app, hit)            

        return moved

def forwardHitToServer(app, hitChar):
    if hitChar == None or not isinstance(hitChar, Character):
        return

    mpid = hitChar.mesh.data.get("mpid", None)
    if mpid == None:
        return

    info = {f"{mpid}health": hitChar.health}
    net.sendInfo(info, app.conn)

def updateServerInfo(app):
    info = {"pos": app.cam, "dir": app.camDir, "health": app.health}
    net.sendInfo(info, app.conn)

def multiplayer_timerFired(app):
    deltaTime = time.time() - app.lastTimerTime
    fpsGameProcess(app, deltaTime)

    if app.msgMovementAllowed:
        moved = processKeys(app, deltaTime)
        if moved: 
            updateServerInfo(app)

    if app.stateChanged:
        gameStateChanged(app)

    app.lastTimerTime = time.time()


def multiplayer_redrawAll(app, canvas):
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
