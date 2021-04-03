from dataclasses import dataclass

from cmu_112_graphics import *

import numpy as np
import math, time

import ply_importer

from threedee import *

def clamp(x, low, high):
    return max(low, min(x, high))

def rgbToHex(r, g, b):
    r = clamp(int(r), 0, 255)
    g = clamp(int(g), 0, 255)
    b = clamp(int(b), 0, 255)
    return f'#{r:02x}{g:02x}{b:02x}'


def appStarted(app):
    app.model = ply_importer.importPly("diamonti.ply")
    app.cam = Vector3D.fromCoords(0, 0, 0)
    app.light = Vector3D.fromCoords(0, 0, -1)

    targetFps = 144
    app.timerDelay = 1000//targetFps
    app.started = time.time()

def drawPolygon(app, canvas, polygon, color):
    v0 = polygon[0]
    v1 = polygon[1]
    v2 = polygon[2]

    canvas.create_polygon(v0.x(), v0.y(), v1.x(), v1.y(), v2.x(), v2.y(), 
                        outline=color, fill=color)

def paintersAlgorithm(polyAndColor):
    poly = polyAndColor[0]
    return sum(vector.z() for vector in poly)/3

def redrawAll(app, canvas):
    startTime = time.time()

    readyPolys = []
    for poly in app.model.polys:
        projectedPoly = []

        pr, pg, pb = 0, 0, 0

        for i, vec in enumerate(poly):
            vector = copy.deepcopy(vec)

            # Rotation
            theta = 20.0 * (time.time()-app.started)
            theta2 = theta
            vector.rotate(theta, theta2, 0)

            # Translation
            vector.translate(0, 0, 4)

            if vector.hasNormals:
                # Culling
                camDiff = vector-app.cam
                camdp = np.dot(vector.normVector[0:3], camDiff.vector[0:3])
                if camdp > 0:
                    break
                
                # Flat lighting
                r, g, b = 0, 162, 255
                lightdp = np.dot(vector.normVector[0:3], app.light.vector[0:3])
                r *= lightdp
                g *= lightdp
                b *= lightdp
                # I straight up have no idea what I did with this color code
                # It only works this way and im scared to change it now
                pr = r
                pg = g
                pb = b

            # Projection
            fov = 90
            vector.project(app.height, app.width, fov)

            # Normalization
            vector.normalizeToTkinter(app.height, app.width)

            projectedPoly.append(vector)

        if len(projectedPoly) == 3:
            readyPolys.append((projectedPoly, rgbToHex(pr, pg, pb)))
    
    # Draw in order with painter's algorithm
    readyPolys.sort(key=paintersAlgorithm)

    # print([x[0][0].z for x in readyPolys])

    for poly, color in readyPolys:
        drawPolygon(app, canvas, poly, color)

    canvas.create_text(10, 10, text=int(1/(time.time()-startTime)), anchor="nw")

# main
def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
