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
            self.mesh.color = Color(0, 0, 0)


@dataclass
class MazeInfo:
    row: int
    col: int
    dirs: list

# Returns addedCharacters (meshes is destructively modified)
def populateMazeWithEnemies(maze, meshes, roomHeight, roomWidth):
    enemyChance = 70 # 70% chance to have enemies
    maxNumberOfEnemies = 3

    enemyTranslateY = -3

    enemies = []

    rows = len(maze)
    cols = len(maze[0])
    for row in range(rows):
        for col in range(cols):
            willEvenHaveEnemies = random.randint(0, 100)
            if willEvenHaveEnemies > enemyChance:
                continue

            numberOfEnemies = random.randint(1, maxNumberOfEnemies)
            successCount = 0
            while successCount < numberOfEnemies:
                newEnemy = Character(importPly("res/char.ply"))

                # Give the enemy a random position in the room
                xPos, yPos = random.random(), random.random()
                newEnemy.mesh.translate(roomHeight*(row+xPos), enemyTranslateY, roomWidth*(col+yPos))

                # Set mazeinfo for rendering shortcuts
                mazeInfo = MazeInfo(row, col, maze[row][col].dirs)
                newEnemy.mesh.data["mazeinfo"] = mazeInfo

                # Make sure its not colliding with anything else
                if not meshCollidesWithOtherMeshes(newEnemy.mesh, meshes):
                    enemies.append(newEnemy)
                    meshes.append(newEnemy.mesh)
                    successCount += 1

    return enemies


def createMaze(rows, cols, roomHeight, roomWidth, roomDepth):
    maze = genMaze(rows, cols)
    meshes = []
    for row in range(rows):
        for col in range(cols):
            room = createRoom(roomHeight, roomWidth, roomDepth, maze[row][col].dirs)
            mazeInfo = MazeInfo(row, col, maze[row][col].dirs)
            list(map(lambda mesh: mesh.translate(roomHeight*row, 0, roomWidth*col), room))
            list(map(lambda mesh: modifyDict(mesh.data, "mazeinfo", mazeInfo), room))
            meshes.extend(room)

    return maze, meshes

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
    list(map(lambda mesh: mesh.translate(0, 0, width), plane1))

    list(map(lambda mesh: mesh.rotateY(90), plane2))
    list(map(lambda mesh: mesh.translate(height, 0, 0), plane2))

    list(map(lambda mesh: mesh.rotateY(90), plane3))

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
    # after modifying polygons in place, recalculate hitboxes
    [plane.calcCollisionParameters() for plane in planes]

    return planes

def createQuadPlane(height, width, widthOffset = 0):
    meshes = []

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

    mesh = Mesh([(poly0, norm), (poly1, np.copy(norm))], True, True)
    meshes.append(mesh)
    return meshes