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

    app.maze = None

    # State-holding info that needs to be initialized before the recv thread
    app.stateBacklog = []
    app.stateChanged = False

    # Server connection and network setup
    try:
        app.conn = net.connectToServer(app.mpAddr, app.mpPort)

        app.netThread = threading.Thread(target=clientThread, args=(app,))
        app.netThread.start()
        # Show intro message for this gamemode
        showMsg(app, "Welcome to multiplayer.", 3)
    except Exception as e:
        app.conn = None
        showMsg(app, f"Encountered error: {e}", 3, True, False)



    # Multiplayer game logic

    app.respawnTimer = None
    app.respawnInvicibilityTil = None
    app.spawnPoints = [(np.array([10, 4, 10, 0], dtype=np.float64), 270),
                       (np.array([90, 4, 190, 0], dtype=np.float64), 180)]
                    #    (np.array([90, 4, 10, 0], dtype=np.float64), 90),
                    #    (np.array([10, 4, 190, 0], dtype=np.float64), 180)]

    spawnAtASpawnPoint(app)

    pygame.mixer.music.load("res/d_e1m2.mp3")
    pygame.mixer.music.play(-1)


# https://realpython.com/intro-to-python-threading/
def clientThread(app):
    buf = bytearray()
    alreadyReadBuffer = []
    maybeReadables = [app.conn]
    while True:
        result = net.recvMsg(maybeReadables[0], buf)
        # Disconnect on EOF
        if result == "EOF":
            app.conn.close()
            print(f"Disconnected from server!")
            return
        elif isinstance(result, list):
            app.stateBacklog.extend(result)
            app.stateChanged = True

def refreshGameState(app, state):
    #idt is id but python already stole id >:(
    # make list of ids from state
    stateIdts = []
    for key in state:
        found = False
        if "pos" in key:
            idt = int(key[0])
            if not idt in stateIdts:
                stateIdts.append(idt)
        elif "fired" in key:
            app.weapons[state[key]].playSound()

    for key in state:
        for idt in stateIdts:
            if str(idt) not in key and "health" in key:
                if state[key] == app.health:
                    continue
                if app.respawnInvicibilityTil != None and time.time() < app.respawnInvicibilityTil:
                    updateServerInfo(app)
                    continue
                if state[key] > 0 and state[key] < app.health:
                    app.hurtSound.play()

                app.health = state[key]
                if app.health <= 0:
                    app.health = 0
                    app.dead = True
                    showMsg(app, "You died.", 2, False, False)
                    app.deathSound.play()
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
        char.mesh.moveTo(state[posKey][0], state[posKey][1], state[posKey][2]) # -4 adjustment for height difference (this is silly)
        char.facePoint(state[posKey]+state[dirKey])
        _drop = char.setHealth(state[str(charIdt) + "health"])

    # This is still the deletion bit obviously
    for char in toRemove:
        app.chars.remove(char)

def handleStateChange(app):
    loopedCount = 0 # I actually dont trust len in this async situation
    for state in app.stateBacklog:
        loopedCount += 1
        refreshGameState(app, state)

    app.stateBacklog = app.stateBacklog[loopedCount:]
    app.stateChanged = False

def multiplayer_appStopped(app):
    tryEndingConnection(app)

def tryEndingConnection(app):
    if hasattr(app, "conn") and isinstance(app.conn, socket.socket):
        print("Killing remaining connection...")
        app.conn.close() # Don't know why this causes exception but oh well

def multiplayer_sizeChanged(app):
    fpsSizeChanged(app)

def multiplayer_keyPressed(app, event):
    key = event.key.lower()
    if key == "escape":
        tryEndingConnection(app)
        app.changeMode(app, "menu")
        
    app.heldKeys.add(key)

def multiplayer_keyReleased(app, event):
    key = event.key.lower()
    if key in app.heldKeys:
        app.heldKeys.remove(key)

def respawn(app):
    app.respawnTimer = None
    app.respawnInvicibilityTil = time.time()+2
    app.msgMovementAllowed = True
    spawnAtASpawnPoint(app)
    app.dead = False
    app.health = 100
    updateServerInfo(app)

def spawnAtASpawnPoint(app):
    loopCount = 0
    while True:
        loopCount += 1
        spawnPoint = random.choice(app.spawnPoints)
        app.cam = spawnPoint[0]
        app.yaw = spawnPoint[1]
        if not ddd.pointCollidesWithOtherMeshes(app.cam, app.drawables, 1):
            break
        if loopCount >= len(app.spawnPoints)*2:
            break

    recalculateCamDir(app)
    updateServerInfo(app)
    


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
        angleStep = app.turnSpeed*speed

        # rotations        
        if "left" in app.heldKeys:
            app.yaw += angleStep
        elif "right" in app.heldKeys:
            app.yaw -= angleStep


        recalculateCamDir(app)

        if "space" in app.heldKeys:
            fired, hit = fireWeapon(app, app.weapons[app.currentWeapon])
            if fired:
                sendFireToServer(app)
            forwardHitToServer(app, hit)

        if "r" in app.heldKeys:
            switchWeapon(app)

        return moved

def forwardHitToServer(app, hitChar):
    if hitChar == None or not isinstance(hitChar, Character):
        return

    mpid = hitChar.mesh.data.get("mpid", None)
    if mpid == None:
        return

    info = {f"{mpid}health": hitChar.health}
    net.sendInfo(info, app.conn)

def sendFireToServer(app):
    info = {"fired": app.currentWeapon}
    net.sendInfo(info, app.conn)

def updateServerInfo(app):
    if app.conn == None:
        return
        
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
        handleStateChange(app)

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
