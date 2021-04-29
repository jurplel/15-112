from dataclasses import dataclass

import random

from ply_importer import importPly

from ddd import *
from maze import genMaze

class Character:
    def __init__(self, mesh: Mesh):
        mesh.data["ischaracter"] = True
        # this is just the color of all characters at the moment
        mesh.color = Color(214, 124, 13)
        self.mesh = mesh
        self.health = 30

    def getHit(self, amt):
        if self.health > 0:
            self.health -= amt
            
        if self.health <= 0:
            self.mesh.visible = False


@dataclass
class MazeInfo:
    row: int
    col: int
    dirs: list

# Returns addedCharacters (meshes is destructively modified)
def populateMazeWithEnemies(maze, mazeColors, meshes, roomHeight, roomWidth):
    enemyChance = 70 # 70% chance to have enemies
    maxNumberOfEnemies = 3

    enemies = []

    rows = len(maze)
    cols = len(maze[0])
    for row in range(rows):
        for col in range(cols):
            # First room should be safe
            if row == 0 and col == 0:
                continue

            willEvenHaveEnemies = random.randint(0, 100)
            if willEvenHaveEnemies > enemyChance:
                continue

            numberOfEnemies = random.randint(1, maxNumberOfEnemies)
            successCount = 0
            while successCount < numberOfEnemies:
                newEnemy = Character(importPly("res/char.ply"))

                # Give the enemy a random position in the room somewhere near the middle
                xPos, yPos = random.uniform(0.3, 0.6), random.uniform(0.25, 0.75)
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
                    successCount += 1

    return enemies


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
def createRoom(height, width, depth, doorways = []):
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