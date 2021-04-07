# Sources
# https://www.scratchapixel.com/
# https://www.youtube.com/watch?v=ih20l3pJoeU (No code copied, just used to push concepts along!)
# https://en.wikipedia.org/wiki/Rotation_matrix
# https://sites.google.com/site/3dprogramminginpython/ (Did not look at any code!!!)
# http://graphics.cs.cmu.edu/nsp/course/15-462/Spring04/slides/06-viewing.pdf

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

def setNewViewMatrix(app):
    app.viewMatrix = getViewMatrix(app.cam, app.cam + app.camDir)

def setNewProjectionMatrix(app):
    app.projectionMatrix = getProjectionMatrix(app.height, app.width, app.near, app.far, app.fov)

def appStarted(app):
    app.model = ply_importer.importPly("diamonti.ply")
    
    app.cam = np.array([0.0, 0.0, 0.0, 0])
    app.camDir = np.array([0.0, 0.0, 1.0, 0])
    app.yaw = 0

    app.light = np.array([0.0, 0.0, -1.0, 0])

    app.fov = 90
    app.near = 0.1
    app.far = 100

    setNewProjectionMatrix(app)
    setNewViewMatrix(app)

    targetFps = 144
    app.timerDelay = 1500//targetFps
    app.started = time.time()
    # app.lastMousePos = None

def sizeChanged(app):
    setNewProjectionMatrix(app)

def keyPressed(app, event):
    key = event.key.lower()

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
        
    yawMatrix = getRotationMatrix(0, app.yaw, 0)
    app.camDir = yawMatrix @ np.array([0, 0, 1, 0])
    setNewViewMatrix(app)
    
        
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
                        outline="black", fill=color)

def paintersAlgorithm(polyAndColor):
    poly = polyAndColor[0]
    return -sum(vector[2] for vector in poly)/3


def redrawAll(app, canvas):
    startTime = time.time()

    # Get matrices once
    # These matrices do not need to be gotten every redraw...
    # world space matrices can be stored in a Mesh/object class
    
    translationMatrix = getTranslationMatrix(0, 0, 4)

    theta = 20.0 * (time.time()-app.started)
    theta2 = theta
    rotationMatrix = getRotationMatrix(theta, theta2, 0)

    transformMatrix = rotationMatrix @ translationMatrix

    mesh = app.model
    newPolys = copy.deepcopy(mesh.polys)
    readyPolys = []
    for poly, norms in newPolys:
        # To world space
        np.matmul(poly, transformMatrix, poly)
        np.matmul(norms, rotationMatrix, norms)

        r, g, b = 0, 162, 255
        if mesh.hasNormals:
            # Culling
            avgNormal = np.add.reduce(norms) / len(norms)
            camRay = poly[0] - app.cam
            camDiff = np.dot(avgNormal, camRay)
            if camDiff > 0:
                continue
            # Flat shading
            lightDiff = max(0.25, np.dot(avgNormal, app.light))
            r *= lightDiff
            g *= lightDiff
            b *= lightDiff

        # To camera space
        np.matmul(poly, app.viewMatrix, poly)

        # Perspective projection to clip space
        np.matmul(poly, app.projectionMatrix, poly)

        # Remove if outside viewing zone
        if clipPoly(poly):
            continue

        # From clip space to normalized projection
        normalizeProjectedPoly(poly)

        # To raster space
        toRasterSpace(poly, app.height, app.width)

        readyPolys.append((poly, rgbToHex(r, g, b)))
    
    # Draw in order with painter's algorithm
    readyPolys.sort(key=paintersAlgorithm) # This is a glitchy algorithm but its good enough

    # List comprehensions are potentially faster than for loops
    [drawPolygon(app, canvas, x[0], x[1]) for x in readyPolys]

    # fps counter
    canvas.create_text(15, 15, text=int(1/(time.time()-startTime)), anchor="nw")

def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

if __name__ == '__main__':
    main()
