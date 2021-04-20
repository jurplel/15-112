from threedee import *

# Returns 4 meshes without doorway, 6 meshes with
def createRoom(height, width, depth, doorway = None):
    plane0 = [createQuadPlane(depth, height)]
    plane1 = [createQuadPlane(depth, height)]
    plane2 = [createQuadPlane(depth, width)]
    plane3 = [createQuadPlane(depth, width)]
    if doorway == Direction.SOUTH:
        plane0 = createDoorway(depth, height)
    elif doorway == Direction.NORTH:
        plane1 = createDoorway(depth, height)
    elif doorway == Direction.EAST:
        plane2 = createDoorway(depth, width)
    elif doorway == Direction.WEST:
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
    plane1.translate((width+doorWidth)/2, 0, 0)
    plane2 = createQuadPlane(height-doorHeight, doorWidth)
    plane2.translate((width-doorWidth)/2, doorHeight, 0)

    planes = [plane0, plane1, plane2]
    # after modifying polygons in place, recalculate hitboxes
    [plane.calcCollisionParameters() for plane in planes]

    return planes

def createQuadPlane(height, width):
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
    return Mesh([(poly0, norm), (poly1, np.copy(norm))], True, True)