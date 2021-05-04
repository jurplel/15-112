import numpy as np
import time

from util import *
import ddd

from maze import drawMazeMap

class Weapon:
    def __init__(self, damage, cooldown):
        self.damage = damage
        self.cooldown = cooldown
        self.dmgFalloff = 50
        self.setSprites(None)
        self.setSound(None)
        self.lastShot = time.time()

    def setSprites(self, sprites = None):
        self.sprites = sprites
        self.hasSprites = False
        if self.sprites != None and isinstance(self.sprites, list):
            self.hasSprites = True
            self.spriteCount = len(sprites)
            self.spriteState = 0

    def setSound(self, sound):
        self.sound = sound
        self.hasSound = False
        if self.sound != None:
            self.hasSound = True

    def playSound(self):
        if self.hasSound and self.sound != None:
            self.sound.play()


def setNewViewMatrix(app):
    app.viewMatrix = ddd.getViewMatrix(app.cam, app.cam + app.camDir)

def setNewProjectionMatrix(app):
    app.projectionMatrix = ddd.getProjectionMatrix(app.height, app.width, app.fov)

def initFps(app):
    app.drawables = []
    app.chars = []
    app.drops = []

    # Listen--I want you to go AS FAST AS POSSIBLE
    app.timerDelay = 1

    # Player parameters
    app.health = 100
    app.dead = False
    app.movementSpeed = 20
    app.hurtCooldown = 400
    app.lastHurt = time.time()

    app.hurtSound = pygame.mixer.Sound("res/dsnoway.wav")
    app.hurtSound.set_volume(app.effectVolume)
    app.deathSound = pygame.mixer.Sound("res/dsplpain.wav")
    app.deathSound.set_volume(app.effectVolume)
    app.hitSound = pygame.mixer.Sound("res/hitsound.wav")
    app.hitSound.set_volume(app.effectVolume)

    # Last hit/damage indicator paremeters
    app.lastHitName = None
    app.lastHitHealth = None
    app.lastHitMaxHealth = None
    app.lastHitTime = time.time()

    # msg parameters
    app.msg = None
    app.msgTime = time.time()
    app.msgReturnToMenu = False
    app.msgMovementAllowed = True

    # Base game logic parameters
    app.heldKeys = set()
    app.started = time.time()
    app.lastTimerTime = time.time()

    # Initialize default player/cam coordinates
    app.cam = np.array([10, 4, 10, 0], dtype=np.float64)
    app.camDir = np.array([0, 0, 1, 0], dtype=np.float64)
    app.yaw = 0

    # Default light direction
    app.light = np.array([1, -0.5, 1, 0], dtype=np.float64)
    ddd.normVec(app.light)

    # Initialize matrices
    setNewProjectionMatrix(app)
    setNewViewMatrix(app)

    # Maze logic
    app.maze = None
    app.roomJustChanged = False

    # Initialize weapons
    app.weapons = []
    app.weaponSwitchTimer = time.time()
    app.currentWeapon = 0
    initPistol(app)
    initShotgun(app)

def fpsSizeChanged(app):
    setNewProjectionMatrix(app)

def recalculateCamDir(app):
    app.camDir = np.array([0, 0, 1, 0]) @ ddd.getYRotationMatrix(app.yaw)
    setNewViewMatrix(app)

def initPistol(app):
    # Parameters
    dmg = 10
    cooldown = 400

    # Sprite
    spritesheet = app.loadImage("res/revolver.png")
    num = 4
    sprites = spritesheetToSprite(spritesheet, 1, num, spritesheet.height, spritesheet.width/num, 2, app.scaleImage)

    # Sound
    sound = pygame.mixer.Sound("res/dspistol.wav")
    sound.set_volume(app.effectVolume)

    # Object
    pistol = Weapon(dmg, cooldown)
    pistol.setSprites(sprites)
    pistol.setSound(sound)

    app.weapons.append(pistol)

def initShotgun(app):
    # Parameters
    dmg = 25
    cooldown = 800

    # Sprite
    spritesheet = app.loadImage("res/spas.png")
    num = 4
    sprites = spritesheetToSprite(spritesheet, 1, num, spritesheet.height, spritesheet.width/num, 2, app.scaleImage)

    # Sound
    sound = pygame.mixer.Sound("res/dsshotgn.wav")
    sound.set_volume(app.effectVolume)

    # Object
    shotgun = Weapon(dmg, cooldown)
    shotgun.setSprites(sprites)
    shotgun.setSound(sound)

    shotgun.dmgFalloff = 8

    app.weapons.append(shotgun)

# Returns (fired, hitCharacter)
def fireWeapon(app, weapon):
    sinceLastFired = time.time() - weapon.lastShot
    if sinceLastFired*1000 < weapon.cooldown:
        return False, None

    weapon.lastShot = time.time()
    if weapon.hasSprites:
        weapon.spriteState = 1
    
    weapon.playSound()
    for char in app.chars:
        hit = ddd.rayIntersectsMeshFirst(char.mesh, app.drawables, 
                                app.cam, app.camDir)
        
        # If the enemy isn't blocked by anything (or close to being blocked by our definition)
        # then the enemy got hit!
        if hit:
            # check if its in the current room too!
            mazeInfo = char.mesh.data.get("mazeinfo", None)
            if mazeInfo != None and (mazeInfo.row, mazeInfo.col) != app.currentRoom:
                return

            app.hitSound.play()

            # Damage falloff calculation
            dist = ddd.vectorDist(char.mesh.avgVec, app.cam[0:3])
            dmgMult = weapon.dmgFalloff/dist
            dmgMult = min(1, dmgMult)

            drop = char.getHit(weapon.damage*dmgMult)
            if drop != None:
                if drop.sound != None:
                    drop.sound.set_volume(app.effectVolume)
                
                if drop.mesh.data["pickup"] == "win":
                    drop.pickupCallback = lambda pos: pickupWin(app, pos)
                elif drop.mesh.data["pickup"] == "health":
                    drop.pickupCallback = lambda pos: pickupHealth(app)
                app.drops.append(drop)
                app.drawables.append(drop.mesh)

            # Set damage indicator variables
            app.lastHitName = char.name
            app.lastHitHealth = char.health
            app.lastHitMaxHealth = char.maxHealth
            app.lastHitTime = time.time()+3
            return True, char

    return True, None

def switchWeapon(app):
    if time.time() < app.weaponSwitchTimer:
        return

    app.currentWeapon += 1
    if app.currentWeapon >= len(app.weapons):
        app.currentWeapon = 0

    app.weaponSwitchTimer = time.time()+0.2

def pickupWin(app, pos):
    showMsg(app, "You win!", 3, True, True)

def pickupHealth(app):
    app.health += 50
    if app.health > 100:
        app.health = 100

def getHurt(app, amount):
    if app.health <= 0:
        return

    sinceLastHurt = time.time() - app.lastHurt
    if sinceLastHurt*1000 < app.hurtCooldown:
        return

    app.health -= amount

    if app.health <= 0:
        app.health = 0
        app.dead = True
        app.deathSound.play()
        showMsg(app, "You died.", 3, True, False)
    else:
        app.hurtSound.play()

    app.lastHurt = time.time()

def setCurrentRoom(app):
    if app.maze == None:
        return

    row = int(app.cam[0] / app.roomHeight)
    col = int(app.cam[2] / app.roomWidth)
    newRoom = True if (row, col) != app.currentRoom else False
    app.roomJustChanged = newRoom

    app.currentRoom = row, col

    for mesh in app.drawables:
        if app.currentRoom != None and mesh.data.get("mazeinfo", None) != None:
            meshMazeInfo = mesh.data.get("mazeinfo", None)
            
            if meshMazeInfo != None:
                rowDiff = abs(meshMazeInfo.row - app.currentRoom[0])
                colDiff = abs(meshMazeInfo.col - app.currentRoom[1])
                
                isCurrentRoom = rowDiff == 0 and colDiff == 0

                mesh.toBeDrawn = isCurrentRoom


def redraw3D(app, canvas):
    readyPolys = []
    for mesh in app.drawables:
        readyPolys.extend(mesh.process(app.cam, app.light,
                                        app.height, app.width,
                                        app.projectionMatrix, app.viewMatrix))

    # Clip on screen edges in screen space
    morePolys = ddd.clipAllPolysOnScreenEdgePlanes(readyPolys, app.height, app.width)
    readyPolys.extend(morePolys)

    # Draw in order with painter's algorithm
    readyPolys.sort(key=ddd.paintersAlgorithm)

    # List comprehensions are potentially faster than for loops
    [ddd.tkDrawPolygon(app, canvas, x[0], x[1]) for x in readyPolys]

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

def drawWeaponSprite(app, canvas):
    if app.dead:
        return
         
    weapon = app.weapons[app.currentWeapon]
    if weapon.hasSprites:
        sprite = weapon.sprites[int(weapon.spriteState)]
        canvas.create_image(app.width/2+sprite.width()/10, app.height-sprite.height()/2, image=sprite)

def drawHealthAndMinimap(app, canvas):
    healthX = app.hudMargin
    healthY = app.height-app.hudMargin
    healthW = 200
    healthH = 20
    marginWidth = 6

    healthColor = "lawn green" if app.health > 25 else "tomato2" # Why do i always choose the weird colors

    if (hasattr(app, "maze") and app.maze != None and 
        hasattr(app, "mazeCols") and hasattr(app, "mazeRows") and 
        hasattr(app, "currentRoom")):
        drawMazeMap(app, canvas, healthX, healthY-healthW, healthX+healthW, 
                                                healthY-healthH, "gray60", "gray25", app.currentRoom, healthColor)
    

    canvas.create_rectangle(healthX, healthY-healthH, healthX+healthW*(app.health/100), healthY, width=0, fill=healthColor)
    canvas.create_rectangle(healthX+marginWidth/2, healthY-healthH, healthX+healthW-marginWidth/2, healthY, width=marginWidth, outline="gray25")

def drawDamageIndicator(app, canvas):
    # Damage indicator
    if app.lastHitName == None:
        return
        
    marginWidth = 6
    indicatorW = 200
    indicatorH = 20
    indicatorX = app.width-app.hudMargin-indicatorW
    indicatorY = app.hudMargin
    enemyHealthColor = "lawn green" if app.lastHitHealth > app.lastHitMaxHealth*0.25 else "tomato2"
    canvas.create_rectangle(indicatorX, indicatorY, indicatorX+indicatorW, indicatorY+indicatorH*3, fill= "gray60", width=marginWidth, outline="gray25")

    canvas.create_text(indicatorX+marginWidth, indicatorY+marginWidth, 
                        text=f"{app.lastHitName}\n", anchor="nw", font="Ubuntu 14 italic", fill="black")

    canvas.create_rectangle(indicatorX, indicatorY+indicatorH*2, indicatorX+indicatorW*(app.lastHitHealth)/app.lastHitMaxHealth, 
                            indicatorY+indicatorH*3, width=0, fill=enemyHealthColor, outline="gray25")
                            
    canvas.create_rectangle(indicatorX, indicatorY+indicatorH*2, indicatorX+indicatorW, indicatorY+indicatorH*3, outline="gray25", width=marginWidth)

# stipple from https://stackoverflow.com/questions/15468327/how-can-i-vary-a-shapes-alpha-with-tkinter
def drawHud(app, canvas):
    drawHealthAndMinimap(app, canvas)
    drawDamageIndicator(app, canvas)
    
    if app.drawCrosshair:
        r = 2
        canvas.create_rectangle(app.width/2-r, app.height/2-r, app.width/2+r, app.height/2+r,
            fill="white", width=1, outline="black")

def drawMsg(app, canvas):
    if app.msg:
        ry = 20
        ry *= len(app.msg.splitlines())
        longestLineLen = 0

        for line in app.msg.splitlines():
            if len(line) > longestLineLen:
                longestLineLen = len(line)

        rx = 10
        rx *= longestLineLen

        canvas.create_rectangle(app.width/2-rx, app.height/2-ry, app.width/2+rx, app.height/2+ry, fill="white", outline="black", stipple="gray50")
        canvas.create_text(app.width/2, app.height/2, text=app.msg, font="Ubuntu 24 italic", fill="black")

def fpsGameProcess(app, deltaTime):
    roomJustChanged = False
    processMsg(app)
    processWeapons(app, deltaTime)
    processLastHit(app)
    processDrops(app, deltaTime)

def processMsg(app):
    if app.msg != None and app.msgTime-time.time() < 0:
        app.msg = None
        if app.msgReturnToMenu:
            app.changeMode(app, "menu")

def processWeapons(app, deltaTime):
    for weapon in app.weapons:
        if weapon.hasSprites and weapon.spriteState > 0:
            weapon.spriteState += 10*deltaTime
            if weapon.spriteState >= weapon.spriteCount:
                weapon.spriteState = 0

def processLastHit(app):
    if app.lastHitTime < time.time():
        app.lastHitName = None
        app.lastHitHealth = None
        app.lastHitMaxHealth = None

def processDrops(app, deltaTime):
   for drop in app.drops:
        if drop.mesh.toBeDrawn == False:
            continue
        mazeInfo = drop.mesh.data.get("mazeinfo", None)
        
        if mazeInfo == None or (mazeInfo.row, mazeInfo.col) == app.currentRoom:
            drop.process(app.cam, deltaTime)

# drz/drx is delta relative z/x
def relativeCamMove(app, drz, drx):
    oldCam = copy.deepcopy(app.cam)
    app.cam += app.camDir * drz

    sidewaysCamDir = app.camDir @ ddd.getRotationMatrix(0, 90, 0)

    app.cam += sidewaysCamDir * drx

    # Check a shorter distance for low framerates
    # It's still possible to clip through walls but much harder with this
    testdrz = min(min(drz, 0.2), max(drz, -0.2), key=abs)
    testdrx = min(min(drx, 0.2), max(drx, -0.2), key=abs)
    testCam = copy.deepcopy(oldCam) + app.camDir * testdrz
    testCam += sidewaysCamDir * testdrx

    # You can't walk through walls
    if (ddd.pointCollidesWithOtherMeshes(testCam, app.drawables, 1) or
        ddd.pointCollidesWithOtherMeshes(app.cam, app.drawables, 1)):
        app.cam = oldCam
        return False

    setCurrentRoom(app)
    return True
    

def showMsg(app, msg, delay = 3, returnToMenu = False, allowMovement = True):
    if app.msg != None:
        return

    app.msg = msg
    app.msgTime = time.time()+delay
    app.msgReturnToMenu = returnToMenu
    app.msgMovementAllowed = allowMovement