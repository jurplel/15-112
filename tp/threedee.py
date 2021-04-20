# https://www.youtube.com/watch?v=ih20l3pJoeU
# ^ This video was broadly followed and helped me to form the structure of the program
# https://www.scratchapixel.com/ <-- Lots of stuff from there too

from dataclasses import dataclass
from enum import Enum

import numpy as np
import math, copy

from util import *

class Mesh:
    def __init__(self, polys, hasNormals):
        self._polys = polys
        self.calcCollisionParameters()
        self.hasNormals = hasNormals
        self.translationMatrix = getTranslationMatrix(0, 0, 2)
        self.rotationMatrix = getRotationMatrix(0, 0, 0)
        self.transformMatrix = self.rotationMatrix @ self.translationMatrix
        self.color = Color(0, 162, 255)

    @property
    def polys(self):
        return self._polys

    @polys.setter
    def polys(self, new_value):
        self._polys = new_value
        self.calcCollisionParameters()

    def calcCollisionParameters(self):
        allX = []
        allY = []
        allZ = []
        for poly, _norm in self._polys:
            allX.extend(poly[:,0])
            allY.extend(poly[:,1])
            allZ.extend(poly[:,2])

        self.maxX = max(allX)
        self.minX = min(allX)
        self.maxY = max(allY)
        self.minY = min(allY)
        self.maxZ = max(allZ)
        self.minZ = min(allZ)

    def translate(self, x, y, z):
        translationMatrix = getTranslationMatrix(x, y, z)
        for poly, _norm in self.polys:
            np.matmul(poly, translationMatrix, poly)
        self.calcCollisionParameters()

    def rotateX(self, degX):
        rotationMatrix = getXRotationMatrix(degX)
        for poly, norm in self.polys:
            np.matmul(poly, rotationMatrix, poly)
            np.matmul(norm, rotationMatrix, norm)
        self.calcCollisionParameters()

    def rotateY(self, degY):
        rotationMatrix = getYRotationMatrix(degY)
        for poly, norm in self.polys:
            np.matmul(poly, rotationMatrix, poly)
            np.matmul(norm, rotationMatrix, norm)
        self.calcCollisionParameters()

    def rotateZ(self, degZ):
        rotationMatrix = getZRotationMatrix(degZ)
        for poly, norm in self.polys:
            np.matmul(poly, rotationMatrix, poly)
            np.matmul(norm, rotationMatrix, norm)
        self.calcCollisionParameters()

    # Returns list of "processed" polys (Ready for drawing)
    # order mostly from https://www.youtube.com/watch?v=ih20l3pJoeU
    def process(self, camPos, lightDir, height, width, projMatrix, viewMatrix):
        newPolys = copy.deepcopy(self.polys)
        readyPolys = []
        for poly, norms in newPolys:
            lightedColor = None
            if self.hasNormals:
                avgNormal = np.add.reduce(norms) / len(norms)
                # Culling
                if cull(avgNormal, poly, camPos):
                    continue

                # Flat shading
                lightFactor = flatLightingFactor(avgNormal, lightDir)
                lightedColor = self.color * lightFactor

            # To camera space
            np.matmul(poly, viewMatrix, poly)

            # Clip against z near clipping plane
            clipResult = nearClipViewSpacePoly(poly)
            if clipResult[0] == False:
                continue
            elif clipResult[0] == True:
                newClipPolys = clipResult[1]
                for newClipPoly in newClipPolys:
                    projectPoly(newClipPoly, projMatrix)
                    toRasterSpace(newClipPoly, height, width)
                    readyPolys.append((newClipPoly, lightedColor.toHex()))

            # Perspective projection
            projectPoly(poly, projMatrix)

            # To raster space
            toRasterSpace(poly, height, width)

            readyPolys.append((poly, lightedColor.toHex()))

        return readyPolys

# https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix
# https://www.youtube.com/watch?v=ih20l3pJoeU
def getProjectionMatrix(height, width, fov = 90):
    far = 100 # Constants i guess idk
    near = 1
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

# https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/lookat-function
# https://learnopengl.com/Getting-started/Camera
# I don't really know where the dot products came from--I think this function's math might be a bit wrong
# That would also explain why pitch doesn't work
# (but messing with it breaks it and yaw works enough so ¯\_(ツ)_/¯)
def getViewMatrix(pos, towards):
    alwaysUpCheat = [0, 1, 0] # this only works if the camera never goes 90deg up or down (gimbal lock)

    zForward = (towards - pos)[0:3]
    normVec(zForward)

    # These are not always perpendicular... (does that matter?)
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

# for citations, see getProjectionMatrix
def projectPoly(poly: np.array, projectionMatrix):
    np.matmul(poly, projectionMatrix, poly)
    # Convert from homogenous projection to normalized projection
    for i, vertex in enumerate(poly):
        w = vertex[3]
        poly[i] /= w

def rotatePoly(rotationMatrix, poly: np.array, norms: np.array, hasNorms):
    np.matmul(poly, rotationMatrix, poly)
    if hasNorms:
        np.matmul(norms, rotationMatrix, norms)

# https://sites.google.com/site/3dprogramminginpython/
# ^Math sorta from there but then I changed it a bit
def toRasterSpace(poly: np.array, height, width):
    addOneMatrix = [1, 1, 0, 0]
    poly += addOneMatrix

    normalizeMatrix = [width/2, height/2, 1, 1]
    poly *= normalizeMatrix

# from https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-plane-and-ray-disk-intersection
def linePlaneIntersection(plane: np.array, planeNorm: np.array, P0, P1):
    rayDir = P1-P0
    t = np.dot((plane-P0), planeNorm)/(np.dot(rayDir, planeNorm))
    P = P0 + rayDir*t
    return P

# Concept from https://www.youtube.com/watch?v=HXSuNxpCzdM
def nearClipViewSpacePoly(poly: np.array, zNear = 1):
    newPolys = []
    clipped = []
    for i, vec in enumerate(poly):
        if vec[2] < zNear:
            clipped.append(i)

    if len(clipped) == 0:
        return (None, None)
    elif len(clipped) == 3:
        return (False, None)

    notClipped = (set([0, 1, 2]) - set(clipped))
    if len(clipped) == 1:
        poly1 = poly[clipped[0]]
        poly2 = poly[notClipped.pop()]
        poly3 = poly[notClipped.pop()]
        intersection1 = linePlaneIntersection([0, 0, zNear], [0, 0, 1], poly1[0:3], poly2[0:3])
        intersection2 = linePlaneIntersection([0, 0, zNear], [0, 0, 1], poly1[0:3], poly3[0:3])
        np.put(poly1, [0, 1, 2], intersection1)
        newPolys.append(np.array([poly1, poly3, np.append(intersection2, 1)]))
    elif len(clipped) == 2:
        poly1 = poly[clipped[0]]
        poly2 = poly[clipped[1]]
        poly3 = poly[notClipped.pop()]
        intersection1 = linePlaneIntersection([0, 0, zNear], [0, 0, 1], poly1[0:3], poly3[0:3])
        intersection2 = linePlaneIntersection([0, 0, zNear], [0, 0, 1], poly2[0:3], poly3[0:3])
        np.put(poly1, [0, 1, 2], intersection1)
        np.put(poly2, [0, 1, 2], intersection2)

    return (True, newPolys)

# https://www.youtube.com/watch?v=XgMWc6LumG4
def cull(avgNormal, poly, camPos):
    camRay = poly[0] - camPos
    camDiff = np.dot(avgNormal, camRay)
    if camDiff > 0:
        return True
    return False

# https://www.youtube.com/watch?v=XgMWc6LumG4
def flatLightingFactor(avgNormal, lightVector):
    return max(0.25, np.dot(avgNormal, lightVector))

# https://www.youtube.com/watch?v=XgMWc6LumG4
def paintersAlgorithm(polyAndColor):
    poly = polyAndColor[0]
    return sum(vector[2] for vector in poly)/3

# Used instead of built in np.linalg.norm for performance reasons
def normVec(vec: np.array):
    magnitude = math.sqrt(vec[0]**2+vec[1]**2+vec[2]**2)
    vec /= magnitude
