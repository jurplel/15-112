from threedee import *

def createRoom(height, width, depth):
    plane0 = createQuadPlane(depth, height)
    plane1 = copy.deepcopy(plane0)

    for poly, norm in plane1.polys:
        for vec in poly:
            vec[2] += width
        
        for vec in norm:
            vec *= -1

    plane2 = createQuadPlane(depth, width)
    rot90 = getYRotationMatrix(90)
    for poly, norm in plane2.polys:
        np.matmul(poly, rot90, poly)
        np.matmul(norm, rot90, norm)
            

    plane3 = copy.deepcopy(plane2)

    for poly, norm in plane2.polys:
        for vec in poly:
            vec[0] += height

    for poly, norm in plane3.polys:
        for vec in norm:
            vec *= -1

    planes = [plane0, plane1, plane2, plane3]
    # after modifying polygons in place, recalculate hitboxes
    [plane.calcCollisionParameters() for plane in planes]

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
    return Mesh([(poly0, norm), (poly1, np.copy(norm))], True)