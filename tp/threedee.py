from dataclasses import dataclass

import numpy as np
import math

class Vector3D:
    def __init__(self, array, normArray = [None]):
        if len(array) == 3:
            array = np.append(array, 1)

        self.hasNormals = normArray[0] != None
        if self.hasNormals:
            if len(normArray) == 3:
                normArray = np.append(normArray, 1)

        self.vector = array
        self.normVector = normArray

    @classmethod
    def fromCoords(cls, x, y, z, nx = None, ny = None, nz = None):
        return cls(np.array([x, y, z, 1]), np.array([nx, ny, nz, 1]))

    def x(self):
        return self.vector[0]

    def y(self):
        return self.vector[1]

    def z(self):
        return self.vector[2]

    def nx(self):
        if self.normVector:
            return self.normVector[0]

    def ny(self):
        if self.normVector:
            return self.normVector[1]

    def nz(self):
        if self.normVector:
            return self.normVector[2]

    def project(self, height, width, fov):
        zFar = 100
        zNear = 0.1
        zDiff = zFar-zNear
        fov = math.radians(90.0)
        aRatio = height/width
        fovCalculation = 1/math.tan(fov/2)

        projectionMatrix = np.array([
            [aRatio*fovCalculation, 0, 0, 0],
            [0, fovCalculation, 0, 0],
            [0, 0, zFar/zDiff, 1],
            [0, 0, -(zFar*zNear)/zDiff, 0]
        ])

        self.vector = self.vector @ projectionMatrix
        w = self.vector[3]
        self.vector[0] = self.vector[0] / w
        self.vector[1] = self.vector[1] / w
        self.vector[2] = self.vector[2] / w

    def translate(self, x, y, z):
        translationMatrix = [x, y, z, 0]
        self.vector = self.vector + translationMatrix
        # if self.hasNormals:
            # self.normVector = self.normVector + translationMatrix

    def rotate(self, degX, degY, degZ):
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
        
        self.vector = self.vector @ rotationMatrix

        if self.hasNormals:
            self.normVector = self.normVector @ rotationMatrix

    def normalizeToTkinter(self, height, width):
        # Tkinter y coordinates are upside-down
        invertYMatrix = [1, -1, 1, 1]
        self.vector = self.vector * invertYMatrix
        
        addOneMatrix = [1, 1, 0, 0]
        self.vector = self.vector + addOneMatrix

        normalizeMatrix = [width/2, height/2, 1, 1]
        self.vector = self.vector * normalizeMatrix

    def __str__(self):
        return f"Vector3D({self.x()}, {self.y()}, {self.z()})"

    def __add__(self, other):
        vec = self.vector + other.vector
        if self.hasNormals and other.hasNormals:
            normVec = self.normVector + other.normVector
        else:
            normVec == None
        return Vector3D(vec, normVec)

    def __sub__(self, other):
        vec = self.vector - other.vector
        if self.hasNormals and other.hasNormals:
            normVec = self.normVector - other.normVector
        else:
            normVec = [None]

        return Vector3D(vec, normVec)



        
        
# def vectorDotProduct(v0: Vector3D, v1: Vector3D):

#     return np.dot(v0.toArray(), v1.toArray())


@dataclass
class Mesh:
    polys: list