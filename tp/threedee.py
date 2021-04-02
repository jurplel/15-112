from dataclasses import dataclass

import numpy as np
import math

class Vector3D:
    def __init__(self, x, y, z, nx = None, ny = None, nz = None):
        self.x = x
        self.y = y
        self.z = z
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.hasNormals = nx != None

    @classmethod
    def fromArray(cls, array):
        return cls(array[0], array[1], array[2])

    def project(self, height, width, fov):
        matrix = np.array([self.x, self.y, self.z, 1])

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

        matrix = matrix @ projectionMatrix
        w = matrix[3]
        self.x = matrix[0] / w
        self.y = matrix[1] / w
        self.z = matrix[2] / w

    def rotX(self, deg):
        matrix = self.toArray()
        if self.hasNormals:
            normalMatrix = self.normalsAsVec().toArray()

        theta = math.radians(deg)

        rotationMatrix = np.array([
            [1, 0, 0],
            [0, math.cos(theta), -math.sin(theta)],
            [0, math.sin(theta), math.cos(theta)]
        ])

        matrix = matrix @ rotationMatrix
        self.x = matrix[0]
        self.y = matrix[1]
        self.z = matrix[2]

        if self.hasNormals:
            normalMatrix = normalMatrix @ rotationMatrix
            self.nx = normalMatrix[0]
            self.ny = normalMatrix[1]
            self.nz = normalMatrix[2]

    def rotY(self, deg):
        matrix = self.toArray()
        if self.hasNormals:
            normalMatrix = self.normalsAsVec().toArray()

        theta = math.radians(deg)

        rotationMatrix = np.array([
            [math.cos(theta), 0, math.sin(theta)],
            [0, 1, 0],
            [-math.sin(theta), 0, math.cos(theta)]
        ])

        matrix = matrix @ rotationMatrix
        self.x = matrix[0]
        self.y = matrix[1]
        self.z = matrix[2]

        if self.hasNormals:
            normalMatrix = normalMatrix @ rotationMatrix
            self.nx = normalMatrix[0]
            self.ny = normalMatrix[1]
            self.nz = normalMatrix[2]

    def rotZ(self, deg):
        matrix = self.toArray()
        if self.hasNormals:
            normalMatrix = self.normalsAsVec().toArray()

        theta = math.radians(deg)

        rotationMatrix = np.array([
            [math.cos(theta), -math.sin(theta), 0],
            [math.sin(theta), math.cos(theta), 0],
            [0, 0, 1]
        ])

        matrix = matrix @ rotationMatrix
        self.x = matrix[0]
        self.y = matrix[1]
        self.z = matrix[2]

        if self.hasNormals:
            normalMatrix = normalMatrix @ rotationMatrix
            self.nx = normalMatrix[0]
            self.ny = normalMatrix[1]
            self.nz = normalMatrix[2]

    def normalizeToTkinter(self, height, width):
        # Tkinter y coordinates are upside-down
        self.y = -self.y
        self.y += 1
        self.y *= 0.5
        self.y *= height

        self.x += 1
        self.x *= 0.5
        self.x *= width

    def normalsAsVec(self):
        if self.hasNormals:
            return Vector3D(self.nx, self.ny, self.nz)

    def toList(self):
        return [self.x, self.y, self.z]

    def toArray(self):
        return np.array([self.x, self.y, self.z])

    def __str__(self):
        return f"Vector3D({self.x}, {self.y}, {self.z})"

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Vector3D(x, y, z)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        return Vector3D(x, y, z)



        
        
def vectorDotProduct(v0: Vector3D, v1: Vector3D):

    return np.dot(v0.toArray(), v1.toArray())


@dataclass
class Mesh:
    polys: list