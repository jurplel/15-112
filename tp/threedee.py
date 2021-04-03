from dataclasses import dataclass

import numpy as np
import math, copy

# poly is a np.array of vectors (also np.arrays)
def translatePoly(poly: np.array, x, y, z):
    translationMatrix = [x, y, z]
    poly += translationMatrix
    
def rotatePoly(poly: np.array, degX, degY, degZ):
    alpha = math.radians(degX)
    beta = math.radians(degY)
    gamma = math.radians(degZ)
    
    rotXMatrix = np.array([
        [1, 0, 0],
        [0, math.cos(alpha), -math.sin(alpha)],
        [0, math.sin(alpha), math.cos(alpha)]
    ])
    rotYMatrix = np.array([
        [math.cos(beta), 0, math.sin(beta)],
        [0, 1, 0],
        [-math.sin(beta), 0, math.cos(beta)]
    ])
    rotZMatrix = np.array([
        [math.cos(gamma), -math.sin(gamma), 0],
        [math.sin(gamma), math.cos(gamma), 0],
        [0, 0, 1]
    ])
    rotationMatrix = rotXMatrix @ rotYMatrix @ rotZMatrix

    np.matmul(poly, rotationMatrix, poly)

# Ahh, nasty! Fix this!
zFar = 100
zNear = 0.1
zDiff = zFar-zNear
fov = math.radians(90.0)
fovCalculation = 1/math.tan(fov/2)

PROJECTION_MATRIX = np.array([
    [fovCalculation, 0, 0, 0],
    [0, fovCalculation, 0, 0],
    [0, 0, zFar/zDiff, 1],
    [0, 0, -(zFar*zNear)/zDiff, 0]
])

def updateProjection(height, width):
    aRatio = height/width
    PROJECTION_MATRIX[0][0] = PROJECTION_MATRIX[1][1]*aRatio

def projectPoly(poly: np.array, height, width):
    a = np.ones((3,1))
    homoPoly = np.append(poly, a, axis=1)

    np.matmul(homoPoly, PROJECTION_MATRIX, homoPoly)

    for i, vector in enumerate(homoPoly):        
        w = vector[3]
        if w != 0:
            vector /= w

        poly[i][0] = vector[0]
        poly[i][1] = vector[1]
        poly[i][2] = vector[2]

def makePolyDrawable(poly: np.array, height, width):
    # Tkinter y coordinates are upside-down
    invertYMatrix = [1, -1, 1]
    poly *= invertYMatrix

    addOneMatrix = [1, 1, 0]
    poly += addOneMatrix

    normalizeMatrix = [width/2, height/2, 1]
    poly *= normalizeMatrix

@dataclass
class Mesh:
    polys: np.array
    hasNormals: bool