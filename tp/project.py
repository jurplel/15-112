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
    app.model = ply_importer.importPly("cube2.ply")
    app.cam = Vector3D(0, 0, 0)
    app.light = Vector3D(0, 0, -1)

    targetFps = 144
    app.timerDelay = 1000//targetFps
    app.started = time.time()

def drawPolygon(app, canvas, polygon, color):
    v0 = polygon[0]
    v1 = polygon[1]
    v2 = polygon[2]
    # canvas.create_line(v0.x, v0.y, v1.x, v1.y)
    # canvas.create_line(v1.x, v1.y, v2.x, v2.y)
    # canvas.create_line(v2.x, v2.y, v0.x, v0.y)


    canvas.create_polygon(v0.x, v0.y, v1.x, v1.y, v2.x, v2.y, 
                        outline=color, fill=color)

def redrawAll(app, canvas):
    readyPolys = []
    for poly in app.model.polys:
        projectedPoly = []
        r, g, b = 0, 162, 255

        for i, vec in enumerate(poly):
            vector = copy.deepcopy(vec)

            # Rotation
            theta = 20.0 * (time.time()-app.started)
            theta2 = theta
            vector.rotX(theta)
            vector.rotZ(theta2)

            # Translation
            vector.z += 4

            if vector.hasNormals:
                # Culling
                normals = vector.normalsAsVec()
                camDiff = vector-app.cam
                camdp = vectorDotProduct(normals, camDiff)
                if camdp > 0:
                    break
                
                # Lighting (potential for proper smoother lighting later)
                if i == 0:
                    lightdp = vectorDotProduct(normals, app.light)
                    r *= lightdp
                    g *= lightdp
                    b *= lightdp

            # Projection
            fov = 90
            vector.project(app.height, app.width, fov)

            # Normalization
            vector.normalizeToTkinter(app.height, app.width)

            projectedPoly.append(vector)

        if len(projectedPoly) == 3:
            readyPolys.append((projectedPoly, rgbToHex(r, g, b)))
    
    for poly, color in readyPolys:
        drawPolygon(app, canvas, poly, color)

# main
def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
