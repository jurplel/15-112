from dataclasses import dataclass

import random

from ply_importer import importPly

from ddd import *
from maze import genMaze

class Character:
    def __init__(self, health):
        self.mesh = importPly("res/char.ply")
        self.mesh.data["ischaracter"] = True
        self.health = health
        # default color for characters
        self.mesh.color = Color(214, 124, 13)
        

    def getHit(self, amt):
        if self.health > 0:
            self.health -= amt
            
        if self.health <= 0:
            self.mesh.visible = False

class EnemyType(Enum):
    NORMAL = 0
    ADVANCED = 1
    BOSS = 2

    def getARandomHealthValue(self):
        healthRange = (15, 30)
        if self == EnemyType.ADVANCED:
            healthRange = (35, 50)
        elif self == EnemyType.BOSS:
            healthRange = (80, 100)
        return random.randint(healthRange[0], healthRange[1])

    def getScaleFactor(self):
        scale = 1
        if self == EnemyType.ADVANCED:
            scale = 1.3
        elif self == EnemyType.BOSS:
            scale = 1.75
        return scale

class Enemy(Character):
    def __init__(self, enemyType: EnemyType = EnemyType.NORMAL):
        # Set enemy type parameters
        super().__init__(enemyType.getARandomHealthValue())
        self.mesh.scale(enemyType.getScaleFactor(), enemyType.getScaleFactor(), enemyType.getScaleFactor())

    def runAI():
        pass


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
        newEnemy.mesh.rotateY(random.uniform(0, 360))
        
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
    enemyChance = 0.7 # 70% chance to have enemies
    maxNumberOfEnemies = 4

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
                # in rooms with a lot of enemies, there is a chance for an advanced enemy
                if enemyNum > 2 and random.random() > enemyChance:
                    enemyType = EnemyType.ADVANCED
                else:
                    enemyType = EnemyType.NORMAL

                makeRandomEnemyInMazeRoom(maze, meshes, enemies, mazeColors, row, col, roomHeight, roomWidth, enemyType)

    return enemies

def setupFinalRoomOfMaze(maze, mazeColors, meshes, roomHeight, roomWidth):
    enemies = []

    row = len(maze)-1
    col = len(maze[0])-1

    makeRandomEnemyInMazeRoom(maze, meshes, enemies, mazeColors, row, col, roomHeight, roomWidth, EnemyType.BOSS)
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
def createRoom(height, width, depth, doorways = [], floor = False, ceiling = True):
    plane0 = createQuadPlane(depth, height)
    plane1 = createQuadPlane(depth, height)
    plane2 = createQuadPlane(depth, width)
    plane3 = createQuadPlane(depth, width)
    for doorway in doorways:
        if doorway == Direction.WEST:
            plane0 = createDoorway(depth, height)
        elif doorway == Direction.EAST:
            plane1 = createDoorway(depth, height)
        elif doorway == Direction.SOUTH:
            plane2 = createDoorway(depth, width)
        elif doorway == Direction.NORTH:
            plane3 = createDoorway(depth, width)

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

def createDoorway(height, width):
    doorHeight = min(12, height)
    doorWidth = min(8, width)

    plane0 = createQuadPlane(height, (width-doorWidth)/2)
    plane1 = copy.deepcopy(plane0)
    list(map(lambda mesh: mesh.translate((width+doorWidth)/2, 0, 0), plane1))
    plane2 = createQuadPlane(height-doorHeight, doorWidth)
    list(map(lambda mesh: mesh.translate((width-doorWidth)/2, doorHeight, 0), plane2))

    planes = plane0 + plane1 + plane2
    # after modifying polygons in place, recalculate hitboxes (might not even be necessary now)
    [plane.calcCollisionParameters() for plane in planes]

    return planes

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