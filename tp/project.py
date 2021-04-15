# Some sources
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
    app.projectionMatrix = getProjectionMatrix(app.height, app.width, app.fov)

def appStarted(app):
    # app.model = ply_importer.importPly("cube.ply")
    app.model = createQuadPlane(10, 100)
    
    app.cam = np.array([0, 0, 0, 0], dtype=np.float64)
    app.camDir = np.array([0, 0, 1, 0], dtype=np.float64)
    app.yaw = 0
    app.pitch = 0

    app.light = np.array([0, 0, -1, 0])

    app.fov = 90

    app.wireframe = False

    setNewProjectionMatrix(app)
    setNewViewMatrix(app)

    targetFps = 144
    app.timerDelay = 1500//targetFps
    app.started = time.time()
    app.lastTime = time.time()
    app.heldKeys = set()

def sizeChanged(app):
    setNewProjectionMatrix(app)

def keyPressed(app, event):
    key = event.key.lower()
    app.heldKeys.add(key)

def keyReleased(app, event):
    key = event.key.lower()
    app.heldKeys.remove(key)

def mouseMoved(app, event):
    pass
    # if not app.lastMousePos:
    #     app.lastMousePos = event
    #     return

    # dx = app.lastMousePos-event.x
    # dy = app.lastMousePos-event.y

def timerFired(app):
    deltaTime = time.time() - app.lastTime
    speed = deltaTime * 10
    if app.heldKeys:
        # vertex additions
        if "w" in app.heldKeys:
            app.cam += app.camDir * speed
        elif "s" in app.heldKeys:
            app.cam -= app.camDir * speed

        sidewaysRotationMatrix = getRotationMatrix(0, 90, 0)
        sidewaysCamDir = sidewaysRotationMatrix @ app.camDir

        if "a" in app.heldKeys:
            app.cam -= sidewaysCamDir * speed
        elif "d" in app.heldKeys:
            app.cam += sidewaysCamDir * speed
        
        angleStep = 15
        angleStep *= speed

        # rotations
        if "up" in app.heldKeys:
            app.pitch += angleStep
        elif "down" in app.heldKeys:
            app.pitch -= angleStep
        
        if "left" in app.heldKeys:
            app.yaw += angleStep
        elif "right" in app.heldKeys:
            app.yaw -= angleStep

        # gimbal lock prevent
        app.pitch = clamp(app.pitch, -90+15, 90-15)

        app.camDir = np.array([0, 0, 1, 0]) @ getYRotationMatrix(app.yaw)
        app.camDir = getXRotationMatrix(app.pitch) @ app.camDir
        setNewViewMatrix(app)

    app.lastTime = time.time()


def drawPolygon(app, canvas, polygon, color):
    v0 = polygon[0]
    v1 = polygon[1]
    v2 = polygon[2]

    outlineColor = "black" if app.wireframe else color
    canvas.create_polygon(v0[0], v0[1], v1[0], v1[1], v2[0], v2[1], 
                        outline=outlineColor, fill=color)

def paintersAlgorithm(polyAndColor):
    poly = polyAndColor[0]
    return -sum(vector[2] for vector in poly)/3


def redrawAll(app, canvas):
    startTime = time.time()

    # Get matrices once
    # These matrices do not need to be gotten every redraw...
    # world space matrices can be stored in a Mesh/object class
    
    translationMatrix = getTranslationMatrix(0, -4, 4)

    theta = 20.0 * (time.time()-app.started)
    rotationMatrix = getRotationMatrix(0, 160, 0)

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
            avgNormal = np.add.reduce(norms) / len(norms)
            # Culling
            if cull(avgNormal, poly, app.cam):
                continue

            # Flat shading
            lightFactor = flatLightingFactor(avgNormal, app.light)
            r *= lightFactor
            g *= lightFactor
            b *= lightFactor

        # To camera space
        np.matmul(poly, app.viewMatrix, poly)

        # Clip against z near clipping plane
        clipResult = nearClipViewSpacePoly(poly)
        if clipResult[0] == False:
            continue
        elif clipResult[0] == True:
            newClipPolys = clipResult[1]
            for newClipPoly in newClipPolys:
                np.matmul(newClipPoly, app.projectionMatrix, newClipPoly)
                normalizeProjectedPoly(newClipPoly)
                toRasterSpace(newClipPoly, app.height, app.width)
                readyPolys.append((newClipPoly, rgbToHex(r, g, b)))

        # Perspective projection to "homogenous clip space"
        np.matmul(poly, app.projectionMatrix, poly)

        # Convert from clip space to normalized projection
        normalizeProjectedPoly(poly)

        # To raster space
        toRasterSpace(poly, app.height, app.width)


        # Clip polygons outside of the zone
        # clipResult = clipRasterSpacePoly(poly, app.height, app.width)
        # if clipResult[0] == False:
        #     continue
        # elif clipResult[0] == True:
        #     readyPolys.extend([(newClipPoly, rgbToHex(r, g, b)) for newClipPoly in clipResult[1]])

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
