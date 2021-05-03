import numpy as np
import time

from util import *
import ddd

class Weapon:
    def __init__(self, damage, cooldown):
        self.damage = damage
        self.cooldown = cooldown
        self.setSprites(None)
        self.setSound(None)
        self.lastShot = time.time()
        self.current = False

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
            self.sound.start()


def setNewViewMatrix(app):
    app.viewMatrix = ddd.getViewMatrix(app.cam, app.cam + app.camDir)

def setNewProjectionMatrix(app):
    app.projectionMatrix = ddd.getProjectionMatrix(app.height, app.width, app.fov)

def initFps(app):
    app.drawables = []
    app.chars = []
    app.drops = []

    # I want you to go AS FAST AS POSSIBLE
    app.timerDelay = 1

    # Player parameters
    app.health = 100
    app.movementSpeed = 15
    app.hurtCooldown = 400
    app.lastHurt = time.time()

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

    # Options that can be customizable
    app.fov = 90
    app.wireframe = False # I recommend trying this option!
    app.drawFps = True
    app.drawCrosshair = True
    app.hudMargin = 40

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

    # Initialize weapons
    app.weapons = []
    initPistol(app)
    app.weapons[0].current = True

def fpsSizeChanged(app):
    setNewProjectionMatrix(app)

def recalculateCamDir(app):
    app.camDir = np.array([0, 0, 1, 0]) @ ddd.getYRotationMatrix(app.yaw)
    setNewViewMatrix(app)

def initPistol(app):
    # Pistol parameters
    dmg = 10
    cooldown = 400

    # Pistol sprite
    # this sprite from https://forum.zdoom.org/viewtopic.php?f=4&t=15080&hilit=mac&start=32235
    spritesheet = app.loadImage("res/weapon.png")
    sprites = spritesheetToSprite(spritesheet, 1, 4, spritesheet.height, spritesheet.width/4, 2, app.scaleImage)

    # Pistol sound
    sound = Sound("res/dspistol.wav")

    # Pistol object
    pistol = Weapon(dmg, cooldown)
    pistol.setSprites(sprites)
    pistol.setSound(sound)

    app.weapons.append(pistol)

def getHurt(app, amount):
    if app.health <= 0:
        return

    sinceLastHurt = time.time() - app.lastHurt
    if sinceLastHurt*1000 < app.hurtCooldown:
        return

    app.health -= amount

    if app.health <= 0:
        app.health = 0
        showMsg(app, "You died.", 3, True, False)

    app.lastHurt = time.time()

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
    [drawPolygon(app, canvas, x[0], x[1]) for x in readyPolys]

def drawPolygon(app, canvas, polygon, color):
    v0 = polygon[0]
    v1 = polygon[1]
    v2 = polygon[2]

    outlineColor = "black" if app.wireframe else color
    canvas.create_polygon(v0[0], v0[1], v1[0], v1[1], v2[0], v2[1], 
                        outline=outlineColor, fill=color)

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
    for weapon in app.weapons:
        if weapon.current and weapon.hasSprites:
            sprite = weapon.sprites[int(weapon.spriteState)]
            canvas.create_image(app.width/2+sprite.width()/10, app.height-sprite.height()/2, image=sprite)
            return

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
    processMsg(app)
    processWeapons(app, deltaTime)
    processLastHit(app)

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

# drz/drx is delta relative z/x
def relativeCamMove(app, drz, drx):
    oldCam = copy.deepcopy(app.cam)
    app.cam += app.camDir * drz

    sidewaysCamDir = app.camDir @ ddd.getRotationMatrix(0, 90, 0)

    app.cam += sidewaysCamDir * drx

    for mesh in app.drawables:
        if ddd.pointCollision(mesh, app.cam, 1):
            app.cam = oldCam
            return False

    return True
    

def showMsg(app, msg, delay = 3, returnToMenu = False, allowMovement = True):
    if app.msg != None:
        return

    app.msg = msg
    app.msgTime = time.time()+delay
    app.msgReturnToMenu = returnToMenu
    app.msgMovementAllowed = allowMovement