from dataclasses import dataclass

import numpy as np
import math, copy

# poly is a np.array of vectors (also np.arrays)
def getProjectionMatrix(height, width, fov = 90):
    zFar = 100
    zNear = 0.1
    zDiff = zFar-zNear
    fov = math.radians(90.0)
    fovCalculation = 1/math.tan(fov/2)
    aRatio = height/width

    projectionMatrix = np.array([
        [aRatio*fovCalculation, 0, 0, 0],
        [0, fovCalculation, 0, 0],
        [0, 0, zFar/zDiff, 1],
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

def getLookAtMatrix(pos, towards, upward = np.array([0.0, 1.0, 0.0, 1.0])):
    forward = towards - pos
    normVec(forward)
    normVec(upward)

    up = upward-(forward * np.dot(upward, forward))
    normVec(up)
    right = np.append(np.cross(up[0:3], forward[0:3]), 1)

    lookAtMatrix = np.array([
        [right[0], up[0], forward[0], 0],
        [right[1], up[1], forward[1], 0],
        [right[2], up[2], forward[2], 0],
        [np.dot(right, -pos), np.dot(up, -pos), np.dot(forward, -pos), 1]
    ])

    return lookAtMatrix

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

def makePolyDrawable(poly: np.array, height, width):
    # Tkinter y coordinates are upside-down
    invertYMatrix = [1, -1, 1, 1]
    poly *= invertYMatrix

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