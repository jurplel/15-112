import math

import numpy as np

## This file is for math-y 3d-y util functions that are relatively simple and program-agnostic

#
## Matrix stuff
#
def getTranslationMatrix(x, y, z):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [x, y, z, 1]
    ])


# https://en.wikipedia.org/wiki/Rotation_matrix
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

# Just really wanted a variable called xfactor tbh
# https://www.tutorialspoint.com/computer_graphics/3d_transformation.htm
def getScaleMatrix(xFactor, yFactor, zFactor):
    return np.array([
        [xFactor, 0, 0, 0],
        [0, yFactor, 0, 0],
        [0, 0, zFactor, 0],
        [0, 0, 0,       1]
    ])
#
## Plane stuff
#

# from https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-plane-and-ray-disk-intersection
def linePlaneIntersection(plane: np.array, planeNorm: np.array, P0, P1):
    rayDir = P1-P0
    t = np.dot((plane-P0), planeNorm)/(np.dot(rayDir, planeNorm))
    P = P0 + rayDir*t
    return P

# I know this is stackoverflow but this is a brilliantly simple answer
# https://stackoverflow.com/questions/3860206/signed-distance-between-plane-and-point
def pointAndPlaneDist(point: np.array, plane: np.array, planeNorm: np.array):
    return np.dot(planeNorm, point[0:3]-plane[0:3])

# https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_plane#Restatement_using_linear_algebra
# https://tutorial.math.lamar.edu/classes/calciii/eqnsofplanes.aspx
def closestPointOnPlane(point: np.array, plane: np.array, planeNorm: np.array):
    planeScalar = sum(np.multiply(plane, planeNorm))
    pointOnPlane = (point*planeScalar)/(vecMagnitude(point)**2)
    return pointOnPlane

#
## Vector stuff
#

def vectorDist(vec0: np.array, vec1: np.array):
    subbed = vec1-vec0
    return vecMagnitude(subbed)

# Used instead of built in np.linalg.norm for performance reasons
def normVec(vec: np.array):
    vec /= vecMagnitude(vec)

def vecMagnitude(vec: np.array):
    total = 0
    for term in vec:
        total += term**2
    
    return math.sqrt(total)