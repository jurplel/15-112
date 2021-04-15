from dataclasses import dataclass
from enum import Enum

import numpy as np
import math, copy



# poly is a np.array of vectors (also np.arrays)
# https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix
def getProjectionMatrix(height, width, fov = 90):
    far = 100 # Constants i guess idk
    near = 0.1
    diff = far-near
    fov = math.radians(fov)
    fovCalculation = 1/math.tan(fov/2)
    aRatio = height/width

    projectionMatrix = np.array([
        [aRatio*fovCalculation, 0, 0, 0],
        [0, fovCalculation, 0, 0],
        [0, 0, -far/diff, -1],
        [0, 0, -(far*near)/diff, 0]
    ])

    return projectionMatrix

def getTranslationMatrix(x, y, z):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [x, y, z, 1]
    ])

def getXRotationMatrix(degX):
    alpha = math.radians(degX)
    rotXMatrix = np.array([
        [1, 0, 0, 0],
        [0, math.cos(alpha), -math.sin(alpha), 0],
        [0, math.sin(alpha), math.cos(alpha), 0],
        [0, 0, 0, 1]
    ])

    return rotXMatrix

def getYRotationMatrix(degY):
    beta = math.radians(degY)
    rotYMatrix = np.array([
        [math.cos(beta), 0, math.sin(beta), 0],
        [0, 1, 0, 0],
        [-math.sin(beta), 0, math.cos(beta), 0],
        [0, 0, 0, 1]
    ])

    return rotYMatrix

def getZRotationMatrix(degZ):
    gamma = math.radians(degZ)

    rotZMatrix = np.array([
        [math.cos(gamma), -math.sin(gamma), 0, 0],
        [math.sin(gamma), math.cos(gamma), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    return rotZMatrix

def getRotationMatrix(degX, degY, degZ):
    rotXMatrix = getXRotationMatrix(degX)
    rotYMatrix = getYRotationMatrix(degY)
    rotZMatrix = getZRotationMatrix(degZ)

    rotationMatrix = rotXMatrix @ rotYMatrix @ rotZMatrix
    return rotationMatrix

# This is the lookAt matrix
def getViewMatrix(pos, towards):
    alwaysUpCheat = [0, 1, 0] # this only works if the camera never goes 90deg up or down (gimbal lock)

    zForward = (towards - pos)[0:3]
    normVec(zForward)

    # These are not always perpendicular...
    xRight = np.cross(zForward, alwaysUpCheat)
    normVec(xRight)

    yUp = np.cross(xRight, zForward)

    pos = pos[0:3] # This only applies to pos local (not a destructive op)
    
    # Not sure why pos needs to be negated here, but it just does!
    viewMatrix = np.array([
        [xRight[0], xRight[1], xRight[2], 0],
        [yUp[0], yUp[1], yUp[2], 0],
        [zForward[0], zForward[1], zForward[2], 0],
        [np.dot(xRight, -pos), np.dot(yUp, -pos), np.dot(zForward, -pos), 1]
    ])

    return viewMatrix

def rotatePoly(rotationMatrix, poly: np.array, norms: np.array, hasNorms):
    np.matmul(poly, rotationMatrix, poly)
    if hasNorms:
        np.matmul(norms, rotationMatrix, norms)

def normalizeProjectedPoly(poly: np.array):
    for i, vertex in enumerate(poly):
        w = vertex[3]
        poly[i] /= w


# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
# This is for infinite lines, not line segments! This doesn't require parameterization...
def lineLineIntersection(P1, P2, P3, P4):
    x1, y1 = P1[0], P1[1]
    x2, y2 = P2[0], P2[1]
    x3, y3 = P3[0], P3[1]
    x4, y4 = P4[0], P4[1]
    
    # This is just the written out determinant bit from wikipedia!
    D = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    Px = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/D
    Py = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/D

    return Px, Py

class Dir(Enum):
    EAST = 0
    WEST = 1
    NORTH = 2
    SOUTH = 3

def getViewportEdgeLineRepr(dir: Dir, height, width):
    if dir == Dir.NORTH:
        return (0, 0), (width, 0)
    elif dir == Dir.EAST:
        return (width, 0), (width, height)
    elif dir == Dir.SOUTH:
        return (0, height), (width, height)
    elif dir == Dir.WEST:
        return (0, 0), (0, height)

    raise Exception("Bad direction for getViewportEdgeLineRepr!")

def outsideViewport(vec: np.array, dir: Dir, height, width):
    if dir == Dir.NORTH:
        return vec[1] < 0
    elif dir == Dir.EAST:
        return vec[0] > width
    elif dir == Dir.SOUTH:
        return vec[1] > height
    elif dir == Dir.WEST:
        return vec[0] < 0

    raise Exception("Bad direction for getViewportEdgeLineRepr!")

def linePlaneIntersection(plane: np.array, planeNorm: np.array, P1, P2):
    normalizeProjectedPoly(planeNorm)

def clipRasterSpacePoly(poly: np.array, height, width):

    newPolys = []
    for dir in Dir:
        clipped = []
        for i, vec in enumerate(poly):
            if outsideViewport(vec, dir, height, width):
                clipped.append(i)

        if len(clipped) == 0:
            continue
        elif len(clipped) == 3:
            return (False, None)

        notClipped = (set([0, 1, 2]) - set(clipped))
        VP1, VP2 = getViewportEdgeLineRepr(dir, height, width)
        if len(clipped) == 1:
            P1 = poly[clipped[0]]
            P2 = poly[notClipped.pop()]
            P3 = poly[notClipped.pop()]
            intersection1 = lineLineIntersection(P1, P2, VP1, VP2)
            intersection2 = lineLineIntersection(P1, P3, VP1, VP2)
            poly[clipped[0]][0] = intersection1[0]
            poly[clipped[0]][1] = intersection1[1]
            newPolys.append(np.array([P1, P3, np.append(intersection2, P1[2])], dtype=object))
            clipRasterSpacePoly

        elif len(clipped) == 2:
            # Modify existing polygon to intersection points
            P1 = poly[clipped[0]]
            P2 = poly[clipped[1]]
            P3 = poly[notClipped.pop()]
            intersection1 = lineLineIntersection(P1, P3, VP1, VP2)
            intersection2 = lineLineIntersection(P2, P3, VP1, VP2)
            poly[clipped[0]][0] = intersection1[0]
            poly[clipped[0]][1] = intersection1[1]
            poly[clipped[1]][0] = intersection2[0]
            poly[clipped[1]][1] = intersection2[1]

    return (True, newPolys)

def nearClipViewSpacePoly(poly: np.array, zNear = 0.1):
    clipped = []
    for i, vec in enumerate(poly):
        if vec[2] < zNear:
            clipped.append(i)

    if len(clipped) == 0:
        return (None, None)
    elif len(clipped) == 3:
        return (False, None)

    notClipped = (set([0, 1, 2]) - set(clipped))
    
    


def toRasterSpace(poly: np.array, height, width):
    addOneMatrix = [1, 1, 0, 0]
    poly += addOneMatrix

    normalizeMatrix = [width/2, height/2, 1, 1]
    poly *= normalizeMatrix

def cull(avgNormal, poly, camPos):
    camRay = poly[0] - camPos
    camDiff = np.dot(avgNormal, camRay)
    if camDiff > 0:
        return True
    return False

def flatLightingFactor(avgNormal, lightVector):
    return max(0.25, np.dot(avgNormal, lightVector))

# Used instead of built in np.linalg.norm for performance reasons
def normVec(vec: np.array):
    magnitude = math.sqrt(vec[0]**2+vec[1]**2+vec[2]**2)
    vec /= magnitude

def createQuadPlane(height, width):
    poly0 = np.array([
        [0, height, 0, 1],
        [width, height, 0, 1],
        [width, 0, 0, 1]
    ], np.float64)
    poly1 = np.array([
        [width, 0, 0, 1],
        [0, 0, 0, 1],
        [0, height, 0, 1]
    ], dtype=np.float64)
    norm = np.tile(np.array([0, 0, 1, 0], dtype=np.float64), (3, 1))
    return Mesh([(poly0, norm), (poly1, np.copy(norm))], True)

@dataclass
class Mesh:
    polys: list
    hasNormals: bool