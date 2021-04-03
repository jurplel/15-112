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
    updateProjection(app.height, app.width)
    app.model = ply_importer.importPly("cube.ply")
    app.cam = np.array([0, 0, 0])
    app.light = np.array([0, 0, -1])

    targetFps = 144
    app.timerDelay = 1000//targetFps
    app.started = time.time()

def sizeChanged(app):
    updateProjection(app.height, app.width)

def drawPolygon(app, canvas, polygon, color):
    v0 = polygon[0]
    v1 = polygon[1]
    v2 = polygon[2]

    canvas.create_polygon(v0[0], v0[1], v1[0], v1[1], v2[0], v2[1], 
                        outline=color, fill=color)

def paintersAlgorithm(polyAndColor):
    poly = polyAndColor[0]
    return sum(vector[2] for vector in poly)/3

def redrawAll(app, canvas):
    startTime = time.time()

    mesh = app.model

    readyPolys = []
    for poly, norms in mesh.polys:
        poly = copy.deepcopy(poly)
        norms = copy.deepcopy(norms)
        # Rotation
        theta = 20.0 * (time.time()-app.started)
        theta2 = theta
        rotatePoly(poly, theta, theta2, 0)
        rotatePoly(norms, theta, theta2, 0)
        # Translation
        translatePoly(poly, 0, 0, 4)

        cull = False
        r, g, b = 0, 162, 255
        if mesh.hasNormals:
            for i in range(len(poly)):
                # Culling
                vec, norm = poly[i], norms[i]
                camDiff = vec-app.cam
                camdp = np.dot(norm, camDiff)
                if camdp > 0:
                    cull = True
                    break
                # Flat lighting
                r, g, b = 0, 162, 255
                lightdp = np.dot(norm, app.light)
                r *= lightdp
                g *= lightdp
                b *= lightdp

        if cull:
            continue

        # Projection
        projectPoly(poly, app.height, app.width)

        # Convert to tkinter coords
        makePolyDrawable(poly, app.height, app.width)

        readyPolys.append((poly, rgbToHex(r, g, b)))
    
    # Draw in order with painter's algorithm
    readyPolys.sort(key=paintersAlgorithm)

    for poly, color in readyPolys:
        drawPolygon(app, canvas, poly, color)

    # fps counter
    canvas.create_text(10, 10, text=int(1/(time.time()-startTime)), anchor="nw")

def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
