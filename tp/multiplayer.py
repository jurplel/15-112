from dddgame import *
from fpsgameutil import *

import net
import threading
import socket

def startMultiplayer(app):
    initFps(app)

    # Build PvP level
    room = createRoom(100, 200, 30, [Direction.EAST], False, False, False)
    list(map(lambda mesh: mesh.setColor(Color(48, 161, 58)), room))

    app.drawables.extend(room)
    
    wall0 = createTwoSidedQuadPlane(10, 60)
    list(map(lambda mesh: mesh.translate(0, 0, 50), wall0))
    wall1 = createTwoSidedQuadPlane(10, 80)
    list(map(lambda mesh: mesh.translate(20, 0, 80), wall1))
    wall2 = createTwoSidedQuadPlane(10, 50)
    list(map(lambda mesh: mesh.rotateY(90), wall2))
    list(map(lambda mesh: mesh.translate(70, 0, 150), wall2))
    walls = wall0 + wall1 + wall2
    list(map(lambda mesh: mesh.setColor(Color(89, 58, 21)), walls))

    app.drawables.extend(walls)

    otherRoom = createRoom(60, 30, 30, [Direction.WEST], False)
    list(map(lambda mesh: mesh.translate(20, 0, 200), otherRoom))
    list(map(lambda mesh: mesh.setColor(Color(92, 28, 166)), otherRoom))
    app.drawables.extend(otherRoom)


    # Server connection and network setup
    try:
        app.conn = net.connectToServer(app.mpAddr, app.mpPort)

        app.netThread = threading.Thread(target=clientThread, args=(app,))
        app.netThread.start()
        updateServerInfo(app)
        # Show intro message for this gamemode
        showMsg(app, "Welcome to multiplayer.", 3)
    except Exception as e:
        showMsg(app, f"Encountered error: {e}", 3, True, False)

    app.state = dict()
    app.stateChanged = False





    # Multiplayer game logic
    app.respawnTimer = None
    app.spawnPoints = [(np.array([10, 4, 10, 0], dtype=np.float64), 270),
                       (np.array([90, 4, 190, 0], dtype=np.float64), 180),
                       (np.array([90, 4, 10, 0], dtype=np.float64), 90),
                       (np.array([10, 4, 190, 0], dtype=np.float64), 180)]


    spawnAtASpawnPoint(app)

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
                if app.health <= 0:
                    app.health = 0
                    app.dead = True
                    showMsg(app, "You died.", 2, False, False)
                    app.respawnTimer = time.time()+2


    # Add any new characters
    for idt in stateIdts:
        found = False
        for char in app.chars:
            mpid = char.mesh.data.get("mpid", None)
            if mpid != None and mpid == idt:
                found = True

        if not found:
            newChar = Character()
            newChar.name = "Player"
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
        char.mesh.moveTo(app.state[posKey][0], app.state[posKey][1], app.state[posKey][2]) # -4 adjustment for height difference (this is silly)
        char.facePoint(app.state[posKey]+app.state[dirKey])
        _drop = char.setHealth(app.state[str(charIdt) + "health"])

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

def respawn(app):
    app.respawnTimer = None
    app.msgMovementAllowed = True
    spawnAtASpawnPoint(app)
    app.dead = False
    app.health = 100
    updateServerInfo(app)

def spawnAtASpawnPoint(app):
    while True:
        spawnPoint = random.choice(app.spawnPoints)
        app.cam = spawnPoint[0]
        app.yaw = spawnPoint[1]
        break
    recalculateCamDir(app)


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

    if app.respawnTimer != None and app.respawnTimer < time.time():
        respawn(app)

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
