from dataclasses import dataclass

import numpy as np
import math, copy

# poly is a np.array of vectors (also np.arrays)
def getProjectionMatrix(height, width, fov = 90):
    zFar = 100
    zNear = 0.1
    zDiff = zFar-zNear
    fov = math.radians(fov)
    fovCalculation = 1/math.tan(fov/2)
    aRatio = height/width

    projectionMatrix = np.array([
        [aRatio*fovCalculation, 0, 0, 0],
        [0, fovCalculation, 0, 0],
        [0, 0, -zFar/zDiff, -1],
        [0, 0, -(zFar*zNear)/zDiff, 0]
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

def projectPoly(projectionMatrix, poly: np.array):
    np.matmul(poly, projectionMatrix, poly)

    for i, vector in enumerate(poly):
        w = vector[3]
        if w == 0:
            break
        poly[i] /= w

def toRasterSpace(poly: np.array, height, width):
    addOneMatrix = [1, 1, 0, 0]
    poly += addOneMatrix

    normalizeMatrix = [width/2, height/2, 1, 1]
    poly *= normalizeMatrix

# Used instead of built in np.linalg.norm for performance reasons
def normVec(vec: np.array):
    magnitude = math.sqrt(vec[0]**2+vec[1]**2+vec[2]**2)
    vec /= magnitude

@dataclass
class Mesh:
    polys: np.array
    hasNormals: bool