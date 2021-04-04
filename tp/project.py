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
    app.model = ply_importer.importPly("cone.ply")
    
    app.cam = np.array([0.0, 0.0, 0.0, 1])
    app.camDir = np.array([0.0, 0.0, 1.0, 1])
    app.yaw = 0

    app.light = np.array([0.0, 0.0, -1.0, 1])

    targetFps = 144
    app.timerDelay = 1500//targetFps
    app.started = time.time()
    app.lastMousePos = None

def sizeChanged(app):
    updateProjection(app.height, app.width)

def keyPressed(app, event):
    key = event.key.lower()

    print(app.cam, app.camDir)
    if key == "w":
        app.cam += app.camDir
    elif key == "s":
        app.cam -= app.camDir
    elif key == "a":
        app.cam[0] -= 1
    elif key == "d":
        app.cam[0] += 1
    elif key == "up":
        app.cam[1] += 1
    elif key == "down":
        app.cam[1] -= 1
    elif key == "left":
        app.yaw -= 15
    elif key == "right":
        app.yaw += 15
        

    rotYMatrix = np.array([
        [math.cos(math.radians(app.yaw)), 0, math.sin(math.radians(app.yaw)), 0],
        [0, 1, 0, 0],
        [-math.sin(math.radians(app.yaw)), 0, math.cos(math.radians(app.yaw)), 0],
        [0, 0, 0, 1]
    ])
    app.camDir = rotYMatrix @ np.array([0, 0, 1, 1])
    
        
def mouseMoved(app, event):
    pass
    # if not app.lastMousePos:
    #     app.lastMousePos = event
    #     return

    # dx = app.lastMousePos-event.x
    # dy = app.lastMousePos-event.y


def drawPolygon(app, canvas, polygon, color):
    v0 = polygon[0]
    v1 = polygon[1]
    v2 = polygon[2]

    canvas.create_polygon(v0[0], v0[1], v1[0], v1[1], v2[0], v2[1], 
                        outline=color, fill=color)

def paintersAlgorithm(polyAndColor):
    poly = polyAndColor[0]
    return -sum(vector[2] for vector in poly)/3


# FURTHER OPTIMIZATION: Allocate one rotation and transform vector for the whole function
# This can be extended to other ones like maybe makepolydrawable?
# Serious excessive allocations right now
# Should probably be put in a drawMesh function with that functionality^
def redrawAll(app, canvas):
    startTime = time.time()

    mesh = app.model
    newPolys = copy.deepcopy(mesh.polys)
    readyPolys = []
    for poly, norms in newPolys:
        # Rotation
        theta = 20.0 * (time.time()-app.started)
        theta2 = theta
        rotatePoly(poly, norms, mesh.hasNormals, theta, theta2, 0)
        # Translation
        translatePoly(poly, 0, 0, 4)

        cullCount = 0
        pr, pg, pb = 0, 0, 0
        if mesh.hasNormals:
            for i in range(len(poly)):
                # Culling
                vec, norm = poly[i], norms[i]
                camDiff = vec-app.camDir
                camdp = np.dot(norm, camDiff)
                if camdp > 0:
                    cullCount += 1
                    break
                # Flat lighting
                r, g, b = 0, 162, 255
                lightdp = np.dot(norm, app.light)-1 # -1 because the 4th parameter makes things weird
                r *= lightdp
                g *= lightdp
                b *= lightdp
                pr += r
                pg += g
                pb += b

        if cullCount == 3:
            continue

        towards = app.cam + app.camDir
        lookAt(poly, app.cam, towards)

        # Projection
        projectPoly(poly, app.height, app.width)

        # Convert to tkinter coords
        makePolyDrawable(poly, app.height, app.width)

        # Avg color
        pr /= 3
        pg /= 3
        pb /= 3
        readyPolys.append((poly, rgbToHex(pr, pg, pb)))
    
    # Draw in order with painter's algorithm
    readyPolys.sort(key=paintersAlgorithm) # This might not even be necessary?

    [drawPolygon(app, canvas, x[0], x[1]) for x in readyPolys]

    # fps counter
    canvas.create_text(15, 15, text=int(1/(time.time()-startTime)), anchor="nw")

def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
