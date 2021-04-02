from dataclasses import dataclass

from cmu_112_graphics import *

import numpy as np
import math, time

import importer

from threedee import Vector3D 


def appStarted(app):
    app.model = importer.importPly("cube.ply")
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
        for i, vertex in enumerate(poly):
            vector = Vector3D.fromArray(vertex)
            theta = 8.0 * (time.time()-app.started)
            theta2 = theta/2
            
            print(theta)
            vector.rotX(theta)
            vector.rotZ(theta2)

            vector.z += 4
            vector.x += 0
            vector.y += 0



            fov = 90

            vector.project(app.height, app.width, fov)

            vector.x += 1
            vector.x *= 0.5
            vector.x *= app.width

            vector.y += 1
            vector.y *= 0.5
            vector.y *= app.height


            projectedPoly.append(vector)
        
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
