from dataclasses import dataclass

from cmu_112_graphics import *

import numpy as np
import math, time

import importer


def appStarted(app):
    app.model = importer.importPly("spherey.ply")
    app.started = time.time()

def drawPolygon(app, canvas, polygon):
    v0 = polygon[0]
    x0 = v0[0]
    y0 = v0[1]
    z0 = v0[2]
    v1 = polygon[1]
    x1 = v1[0]
    y1 = v1[1]
    z1 = v1[2]
    v2 = polygon[2]
    x2 = v2[0]
    y2 = v2[1]
    z2 = v2[2]
    canvas.create_line(x0, y0, x1, y1)
    canvas.create_line(x1, y1, x2, y2)
    canvas.create_line(x2, y2, x0, y0)

def getProjMatrix(app):
    zFar = 100
    zNear = 1
    fov = math.radians(90.0)
    aRatio = app.height/app.width
    projectionMatrix = np.array([
        [aRatio*(1/math.tan(fov/2)), 0, 0, 0],
        [0, 1/math.tan(fov/2), 0, 0],
        [0, 0, zFar/(zFar-zNear), 1],
        [0, 0, -((zFar*zNear)/(zFar-zNear)), 0]
    ])
    return projectionMatrix

def getScreenMatrix(app):
    screenMatrix = [
        [app.width/2, 0, 0, app.width/2],
        [0, -app.height/2, 0, app.height/2],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]
    return screenMatrix

def redrawAll(app, canvas):
    projectionMatrix = getProjMatrix(app)
    screenMatrix = getScreenMatrix(app)
    for poly in app.model.polys:
        projectedPoly = [[], [], [], []]
        for i, vertex in enumerate(poly):
            projectedVertex = np.append(vertex, 1)

            theta = 1.0 * app.started-time.time()
            theta2 = theta/2

            rotZMatrix = [
                [math.cos(theta), math.sin(theta), 0, 0],
                [-math.sin(theta), math.cos(theta), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ]

            rotXMatrix = [
                [1, 0, 0, 0],
                [0, math.cos(theta2), math.sin(theta2), 0],
                [0, -math.sin(theta2), math.cos(theta2), 0],
                [0, 0, 0, 1]
            ]

            projectedVertex = projectedVertex @ rotXMatrix
            projectedVertex = projectedVertex @ rotZMatrix

            projectedVertex[0] += 1.5
            projectedVertex[1] -= 0.5
            projectedVertex[2] += 3

            projectedVertex = projectedVertex @ projectionMatrix
            projectedVertex = projectedVertex @ screenMatrix
            

            projectedPoly[i] = projectedVertex
        
        if not projectedPoly:
            return


        drawPolygon(app, canvas, projectedPoly)

# main
def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
