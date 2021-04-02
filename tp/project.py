from dataclasses import dataclass

from cmu_112_graphics import *

import numpy as np
import math, time

import importer

from threedee import *


def appStarted(app):
    app.model = importer.importPly("cube2.ply")
    app.cam = Vector3D(0, 0, 0)
    targetFps = 144
    app.timerDelay = 1000//targetFps
    app.started = time.time()

def drawPolygon(app, canvas, polygon):
    v0 = polygon[0]
    v1 = polygon[1]
    v2 = polygon[2]
    canvas.create_line(v0.x, v0.y, v1.x, v1.y)
    canvas.create_line(v1.x, v1.y, v2.x, v2.y)
    canvas.create_line(v2.x, v2.y, v0.x, v0.y)

def redrawAll(app, canvas):
    for poly in app.model.polys:
        
        projectedPoly = []
        for i, vec in enumerate(poly):
            vector = copy.deepcopy(vec)

            # Rotation
            theta = 20.0 * (time.time()-app.started)
            theta2 = theta
            vector.rotX(theta)
            vector.rotZ(theta2)

            # Translation
            vector.z += 4

            # Culling
            if vector.hasNormals:
                normals = vector.normalsAsVec()
                camDiff = vector-app.cam
                vdp = vectorDotProduct(normals, camDiff)
                if vdp > 0:
                    break

            # Projection
            fov = 90
            vector.project(app.height, app.width, fov)

            # Normalization
            vector.normalizeToTkinter(app.height, app.width)

            projectedPoly.append(vector)

        if len(projectedPoly) == 3:
            drawPolygon(app, canvas, projectedPoly)

# main
def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
