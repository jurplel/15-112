from dataclasses import dataclass

import numpy as np
import math, copy

# poly is a np.array of vectors (also np.arrays)
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

def getRotationMatrix(degX, degY, degZ):
    alpha = math.radians(degX)
    beta = math.radians(degY)
    gamma = math.radians(degZ)
    
    rotXMatrix = np.array([
        [1, 0, 0, 0],
        [0, math.cos(alpha), -math.sin(alpha), 0],
        [0, math.sin(alpha), math.cos(alpha), 0],
        [0, 0, 0, 1]
    ])
    rotYMatrix = np.array([
        [math.cos(beta), 0, math.sin(beta), 0],
        [0, 1, 0, 0],
        [-math.sin(beta), 0, math.cos(beta), 0],
        [0, 0, 0, 1]
    ])
    rotZMatrix = np.array([
        [math.cos(gamma), -math.sin(gamma), 0, 0],
        [math.sin(gamma), math.cos(gamma), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

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

# https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/projection-matrix-GPU-rendering-pipeline-clipping
# returns true if poly should be skipped
def clipAndNormalizeProjectedPoly(poly: np.array):
    for i, vertex in enumerate(poly):
        w = vertex[3]
        # If outside of view
        if w >= 0 or -w <= vertex[0] <= w:
            return True
        poly[i] /= w

    return False

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
    return Mesh(np.array([(poly0, norm), (poly1, norm)]), True)

@dataclass
class Mesh:
    polys: np.array
    hasNormals: bool