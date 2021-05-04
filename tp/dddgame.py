from dataclasses import dataclass

import random

from ply_importer import importPly

from ddd import *
from maze import genMaze

def isWithinActiveDistance(vec, playerPos, activeDist = 7):
    if vectorDist(vec[0:3], playerPos[0:3]) < activeDist:
        return True
    return False

def dropDiamond(position, color, meshData):
    diamond = Drop(importPly("res/diamonti.ply"))
    diamond.mesh.color = color
    diamond.mesh.scale(2, 2, 2)
    diamond.mesh.data["mazeinfo"] = meshData["mazeinfo"]
    diamond.mesh.data["pickup"] = "win"
    diamond.mesh.translate(position[0], position[1], position[2])
    return diamond

def dropHealth(position, color, meshData):
    heart = Drop(importPly("res/heart.ply"))
    heart.mesh.color = color
    heart.mesh.scale(0.2, 0.2, 0.2)
    heart.mesh.data["mazeinfo"] = meshData["mazeinfo"]
    heart.mesh.data["pickup"] = "health"
    heart.mesh.translate(position[0], position[1], position[2])
    return heart
    
class Drop:
    def __init__(self, mesh, pickupCallback = None):
        self.mesh = mesh
        self.pickupCallback = pickupCallback
        self.rotate = True
        self.rotSpeed = 45
        self.active = True

    def process(self, playerPos, deltaTime):
        if self.rotate and self.mesh.visible and self.mesh.toBeDrawn and self.active:
            self.mesh.rotateY(self.rotSpeed*deltaTime, True)

            if isWithinActiveDistance(self.mesh.avgVec, playerPos):
                if self.pickupCallback != None:
                    self.pickupCallback(self.mesh.avgVec)
                self.mesh.visible = False
                self.active = False

class Character:
    def __init__(self, health = 100):
        self.mesh = importPly("res/char.ply")
        self.mesh.data["ischaracter"] = True
        self.health = health
        self.maxHealth = health
        # default color for characters
        self.mesh.color = Color(214, 124, 13)
        self.lookDir = [0, 0, 1, 0]
        self.deathCallback = None
        self.dead = False
        self.name = "undefined"

    # https://math.stackexchange.com/questions/654315/how-to-convert-a-dot-product-of-two-vectors-to-the-angle-between-the-vectors
    # second answer for formula for angle diff to 2pi
    def facePoint(self, point):
        # 0:3:2 serves to skip the Y coordinate
        toPoint = point[0:3:2]-self.mesh.avgVec[0:3:2]
        
        lookDir2D = self.lookDir[0:3:2]
        normVec(toPoint)
        
        dp = np.dot(lookDir2D, toPoint)
        
        angleDiff = np.arctan2(lookDir2D[0], lookDir2D[1]) - np.arctan2(toPoint[0], toPoint[1])
        
        angleDiff = normAngle(math.degrees(angleDiff), True)
        if abs(angleDiff) < 1:
            return

        self.mesh.rotateY(angleDiff, True)

        self.lookDir = self.lookDir @ getYRotationMatrix(angleDiff)


    def setHealth(self, value):
        self.health = value

        if self.health > 100:
            self.health = 100

        if self.health <= 0:
            avgVec = copy.deepcopy(self.mesh.avgVec)
            self.health = 0
            self.dead = True
            self.mesh.visible = False
            if self.deathCallback != None:
                return self.deathCallback(avgVec, self.mesh.color, self.mesh.data)
        else:
            self.dead = False
            self.mesh.visible = True

    def getHit(self, amt):
        return self.setHealth(self.health-amt)

class EnemyType(Enum):
    NORMAL = 0
    ADVANCED = 1
    BOSS = 2

    def getARandomHealthValue(self):
        healthRange = (15, 30)
        if self == EnemyType.ADVANCED:
            healthRange = (35, 50)
        elif self == EnemyType.BOSS:
            healthRange = (120, 120)
        return random.randint(healthRange[0], healthRange[1])

    def getScaleFactor(self):
        scale = 1
        if self == EnemyType.ADVANCED:
            scale = 1.3
        elif self == EnemyType.BOSS:
            scale = 1.75
        return scale

    def getDamageAmount(self):
        damage = 10
        if self == EnemyType.ADVANCED:
            damage = 15
        elif self == EnemyType.BOSS:
            damage = 20
        return damage

    def getMovementSpeed(self):
        speed = 10
        if self == EnemyType.ADVANCED:
            speed = 12
        elif self == EnemyType.BOSS:
            speed = 14
        return speed

    def getName(self):
        name = "Enemy"
        if self == EnemyType.ADVANCED:
            name = "Advanced Enemy"
        elif self == EnemyType.BOSS:
            name = "The Boss"
        return name
            
class Enemy(Character):
    def __init__(self, enemyType: EnemyType = EnemyType.NORMAL, hitCallback = None):
        # Set enemy type parameters
        super().__init__(enemyType.getARandomHealthValue())
        self.mesh.scale(enemyType.getScaleFactor(), enemyType.getScaleFactor(), enemyType.getScaleFactor())

        self.hitCallback = hitCallback

        self.movementSpeed = enemyType.getMovementSpeed()
        self.dmgAmount = enemyType.getDamageAmount()
        self.name = enemyType.getName()
        
    def moveTowards(self, point, speed):
        toPlayer = point[0:3]-self.mesh.avgVec

        normVec(toPlayer)
        toPlayer *= speed

        self.mesh.translate(toPlayer[0], 0, toPlayer[2])

        if pointCollision(self.mesh, point[0:3], 2):
            self.mesh.translate(-toPlayer[0], 0, -toPlayer[2])
            

    def runAI(self, playerPos, deltaTime):
        self.facePoint(playerPos)

        self.moveTowards(playerPos, deltaTime*self.movementSpeed)

        if isWithinActiveDistance(self.mesh.avgVec, playerPos):
            if self.hitCallback != None:
                self.hitCallback(self.dmgAmount)


@dataclass
class MazeInfo:
    row: int
    col: int
    dirs: list


def makeRandomEnemyInMazeRoom(maze, meshes, enemies, mazeColors, row, col, roomHeight, roomWidth, enemyType: EnemyType = EnemyType.NORMAL):
    while True:
        # Make enemy object with health based on its type (normal, advanced, boss)
        newEnemy = Enemy(enemyType)

        # Give the enemy a random position in the room somewhere kinda near the middle
        xPos, yPos = random.uniform(0.3, 0.6), random.uniform(0.25, 0.75)

        a = random.uniform(0, 360)
        newEnemy.mesh.rotateY(a)
        newEnemy.lookDir = newEnemy.lookDir @ getYRotationMatrix(a)
        
        newEnemy.mesh.translate(roomHeight*(row+xPos), 0, roomWidth*(col+yPos))

        # Set mazeinfo for rendering shortcuts
        mazeInfo = MazeInfo(row, col, maze[row][col].dirs, )
        newEnemy.mesh.data["mazeinfo"] = mazeInfo

        # Set color to opposite of this maze room's color
        newEnemy.mesh.setColor(mazeColors[row][col].complementary())

        # Make sure its not colliding with anything else
        if not meshCollidesWithOtherMeshes(newEnemy.mesh, meshes):
            enemies.append(newEnemy)
            meshes.append(newEnemy.mesh)
            return


# Returns addedCharacters (meshes is destructively modified)
def populateMazeWithEnemies(maze, mazeColors, meshes, roomHeight, roomWidth):
    enemyChance = 0.8 # 70% chance to have enemies
    maxNumberOfEnemies = 6

    enemies = []

    rows = len(maze)
    cols = len(maze[0])
    for row in range(rows):
        for col in range(cols):
            # First room should be safe
            if row == 0 and col == 0:
                continue

            # Last room should be set up manually
            if row == rows-1 and col == cols-1:
                continue

            willEvenHaveEnemies = random.random()
            if willEvenHaveEnemies > enemyChance:
                continue

            numberOfEnemies = random.randint(1, maxNumberOfEnemies)

            for enemyNum in range(numberOfEnemies):
                # in rooms with a lot of enemies, there are chances for an advanced enemy
                drop = None
                if enemyNum > 2 and random.random() > 0.5:
                    enemyType = EnemyType.ADVANCED
                    if random.random() > 0.5: # sometimes advanced guys can drop health powerups
                        drop = dropHealth
                else:
                    enemyType = EnemyType.NORMAL

                makeRandomEnemyInMazeRoom(maze, meshes, enemies, mazeColors, row, col, roomHeight, roomWidth, enemyType)
                if drop != None:
                    enemies[-1].deathCallback = drop

    return enemies

def setupFinalRoomOfMaze(maze, mazeColors, meshes, roomHeight, roomWidth):
    enemies = []

    row = len(maze)-1
    col = len(maze[0])-1

    makeRandomEnemyInMazeRoom(maze, meshes, enemies, mazeColors, row, col, roomHeight, roomWidth, EnemyType.BOSS)
    enemies[-1].deathCallback = dropDiamond
    return enemies

def setupMaze(meshes, rows, cols, roomHeight, roomWidth, roomDepth):
    # Make a maze
    maze, mazeColors, mazeMeshes = createMaze(rows, cols, roomHeight, roomWidth, roomDepth)
    meshes.extend(mazeMeshes)

    # Set up enemies
    enemies = populateMazeWithEnemies(maze, mazeColors, meshes, roomHeight, roomWidth)
    
    # Set up the final room with boss and stuff
    enemies.extend(setupFinalRoomOfMaze(maze, mazeColors, meshes, roomHeight, roomWidth))
    
    return maze, enemies

def createMaze(rows, cols, roomHeight, roomWidth, roomDepth):
    maze = genMaze(rows, cols)
    mazeColors = copy.deepcopy(maze)
    meshes = []
    for row in range(rows):
        for col in range(cols):
            room = createRoom(roomHeight, roomWidth, roomDepth, maze[row][col].dirs)
            mazeInfo = MazeInfo(row, col, maze[row][col].dirs)
            list(map(lambda mesh: mesh.translate(roomHeight*row, 0, roomWidth*col), room))

            randomColor = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            list(map(lambda mesh: modifyDict(mesh.data, "mazeinfo", mazeInfo), room))
            mazeColors[row][col] = randomColor

            list(map(lambda mesh: mesh.setColor(randomColor), room))
            meshes.extend(room)

    return maze, mazeColors, meshes

# Returns 4 meshes without doorway, add 2 for each doorway
def createRoom(height, width, depth, doorways = [], doors = True, floor = False, ceiling = True):
    plane0 = createQuadPlane(depth, height)
    plane1 = createQuadPlane(depth, height)
    plane2 = createQuadPlane(depth, width)
    plane3 = createQuadPlane(depth, width)
    for doorway in doorways:
        if doorway == Direction.WEST:
            plane0 = createDoorway(depth, height)
            if doors:
                plane0.extend(createDoor(height))
        elif doorway == Direction.EAST:
            plane1 = createDoorway(depth, height)
            if doors:
                plane1.extend(createDoor(height))
        elif doorway == Direction.SOUTH:
            plane2 = createDoorway(depth, width)
            if doors:
                plane2.extend(createDoor(width))
        elif doorway == Direction.NORTH:
            plane3 = createDoorway(depth, width)
            if doors:
                plane3.extend(createDoor(width))

    # Since doorway may be a list, all of these planes are stored as lists of meshes
    
    list(map(lambda mesh: mesh.rotateY(180), plane1))
    list(map(lambda mesh: mesh.translate(height, 0, width), plane1))

    list(map(lambda mesh: mesh.rotateY(90), plane2))
    list(map(lambda mesh: mesh.translate(height, 0, 0), plane2))

    list(map(lambda mesh: mesh.rotateY(270), plane3))
    list(map(lambda mesh: mesh.translate(0, 0, width), plane3))

    planes = plane0 + plane1 + plane2 + plane3

    # Floor and ceiling
    if floor:
        plane4 = createQuadPlane(width, height)
        list(map(lambda mesh: mesh.rotateX(90), plane4))
        list(map(lambda mesh: mesh.translate(0, 0, width), plane4))

        planes.extend(plane4)

    if ceiling:
        plane5 = createQuadPlane(width, height)
        list(map(lambda mesh: mesh.rotateX(270), plane5))
        list(map(lambda mesh: mesh.translate(0, depth, 0), plane5))

        planes.extend(plane5)

    return planes

def createDoor(doorwayWidth):
    doorWidth = 8
    meshes = createQuadPlane(12, doorWidth)
    list(map(lambda mesh: modifyDict(mesh.data, "door", True), meshes))
    list(map(lambda mesh: mesh.translate(doorwayWidth/2-doorWidth/2, 0, 0), meshes))
    return meshes

def createDoorway(height, width):
    doorHeight = min(12, height)
    doorWidth = min(8, width)

    plane0 = createQuadPlane(height, (width-doorWidth)/2)
    plane1 = copy.deepcopy(plane0)
    list(map(lambda mesh: mesh.translate((width+doorWidth)/2, 0, 0), plane1))
    plane2 = createQuadPlane(height-doorHeight, doorWidth)
    list(map(lambda mesh: mesh.translate((width-doorWidth)/2, doorHeight, 0), plane2))

    planes = plane0 + plane1 + plane2

    return planes

def createTwoSidedQuadPlane(height, width, maxWidth = 25):
    plane = createQuadPlane(height, width)
    list(map(lambda mesh: mesh.rotateY(180), plane))
    list(map(lambda mesh: mesh.translate(width, 0, 0), plane))
    plane.extend(createQuadPlane(height, width))
    return plane
    

def createQuadPlane(height, width, maxWidth = 25):
    meshes = []
    if maxWidth != None and width > maxWidth:
        meshes.extend(createQuadPlane(height, width-maxWidth, maxWidth))
        for mesh in meshes:
            mesh.translate(maxWidth, 0, 0)

        width = maxWidth

    poly0 = np.array([
        [0, height, 0, 1],
        [width, height, 0, 1],
        [width, 0, 0, 1]
    ], dtype=np.float64)
    poly1 = np.array([
        [width, 0, 0, 1],
        [0, 0, 0, 1],
        [0, height, 0, 1]
    ], dtype=np.float64)

    norm = np.tile(np.array([0, 0, 1, 0], dtype=np.float64), (3, 1))

    mesh = Mesh([(poly0, norm), (poly1, np.copy(norm))], True)
    meshes.append(mesh)
    return meshes