# https://www.youtube.com/watch?v=ih20l3pJoeU
# ^ This video was broadly followed and helped me to form the drawing loop and other foundational things
# https://www.scratchapixel.com/ <-- Lots of stuff from there too

import numpy as np
import math, copy

from util import *

class Mesh:
    def __init__(self, polys, hasNormals, isTwoSided = False):
        self._polys = polys
        self.calcCollisionParameters()
        self.hasNormals = hasNormals
        self.isTwoSided = isTwoSided
        self.color = Color(0, 162, 255)
        self.visible = True
        self.data = dict()

    @property
    def polys(self):
        return self._polys

    @polys.setter
    def polys(self, new_value):
        self._polys = new_value
        self.calcCollisionParameters()

    def calcCollisionParameters(self):
        allX = []
        allY = []
        allZ = []
        for poly, _norm in self._polys:
            allX.extend(poly[:,0])
            allY.extend(poly[:,1])
            allZ.extend(poly[:,2])

        self.maxX = max(allX)
        self.avgX = sum(allX)/len(allX)
        self.minX = min(allX)
        self.maxY = max(allY)
        self.avgY = sum(allY)/len(allY)
        self.minY = min(allY)
        self.maxZ = max(allZ)
        self.avgZ = sum(allZ)/len(allZ)
        self.minZ = min(allZ)

    def translate(self, x, y, z):
        translationMatrix = getTranslationMatrix(x, y, z)
        for poly, _norm in self.polys:
            np.matmul(poly, translationMatrix, poly)
        self.calcCollisionParameters()

    def rotateX(self, degX):
        rotationMatrix = getXRotationMatrix(degX)
        for poly, norm in self.polys:
            np.matmul(poly, rotationMatrix, poly)
            np.matmul(norm, rotationMatrix, norm)
        self.calcCollisionParameters()

    def rotateY(self, degY):
        rotationMatrix = getYRotationMatrix(degY)
        for poly, norm in self.polys:
            np.matmul(poly, rotationMatrix, poly)
            np.matmul(norm, rotationMatrix, norm)
        self.calcCollisionParameters()

    def rotateZ(self, degZ):
        rotationMatrix = getZRotationMatrix(degZ)
        for poly, norm in self.polys:
            np.matmul(poly, rotationMatrix, poly)
            np.matmul(norm, rotationMatrix, norm)
        self.calcCollisionParameters()

    # Returns list of "processed" polys (Ready for drawing)
    # order mostly from https://www.youtube.com/watch?v=ih20l3pJoeU
    def process(self, camPos, lightDir, height, width, projMatrix, viewMatrix):
        if not self.visible:
            return []
        newPolys = copy.deepcopy(self.polys)
        readyPolys = []
        for poly, norms in newPolys:
            lightedColor = None
            if self.hasNormals:
                avgNormal = np.add.reduce(norms) / len(norms)
                # Culling
                if not self.isTwoSided and cull(avgNormal, poly, camPos):
                    continue

                # Flat shading
                lightFactor = flatLightingFactor(avgNormal, lightDir)
                lightedColor = self.color * lightFactor

            # To camera space
            np.matmul(poly, viewMatrix, poly)

            # The end of the polygon processing pipeline--may be run on multiple polygons so thats why its here
            def finishPoly(polyReadyForFinishing):
                projectPoly(polyReadyForFinishing, projMatrix)
                toRasterSpace(polyReadyForFinishing, height, width)
                readyPolys.append((polyReadyForFinishing, lightedColor.toHex()))

            # Clip against z near clipping plane
            clipResult = clipPolyOnNearPlane(poly)
            if clipResult[0] == False:
                continue
            elif clipResult[0] == True:
                newClipPolys = clipResult[1]
                for newClipPoly in newClipPolys:
                    finishPoly(newClipPoly)

            finishPoly(poly)

        return readyPolys

# https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix
# https://www.youtube.com/watch?v=ih20l3pJoeU
def getProjectionMatrix(height, width, fov = 90):
    far = 100 # Constants i guess idk
    near = 2
    diff = far-near
    fov = math.radians(fov)
    fovCalculation = 1/math.tan(fov/2)
    aRatio = height/width

    projectionMatrix = np.array([
        [aRatio*fovCalculation, 0, 0, 0],
        [0, fovCalculation, 0, 0],
        [0, 0, -far/diff, -1],
        [0, 0, -(far*near)/diff, 0]
    ])

    return projectionMatrix

def getTranslationMatrix(x, y, z):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [x, y, z, 1]
    ])


# https://en.wikipedia.org/wiki/Rotation_matrix
def getXRotationMatrix(degX):
    alpha = math.radians(degX)
    rotXMatrix = np.array([
        [1, 0, 0, 0],
        [0, math.cos(alpha), -math.sin(alpha), 0],
        [0, math.sin(alpha), math.cos(alpha), 0],
        [0, 0, 0, 1]
    ])

    return rotXMatrix

def getYRotationMatrix(degY):
    beta = math.radians(degY)
    rotYMatrix = np.array([
        [math.cos(beta), 0, math.sin(beta), 0],
        [0, 1, 0, 0],
        [-math.sin(beta), 0, math.cos(beta), 0],
        [0, 0, 0, 1]
    ])

    return rotYMatrix

def getZRotationMatrix(degZ):
    gamma = math.radians(degZ)

    rotZMatrix = np.array([
        [math.cos(gamma), -math.sin(gamma), 0, 0],
        [math.sin(gamma), math.cos(gamma), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    return rotZMatrix

def getRotationMatrix(degX, degY, degZ):
    rotXMatrix = getXRotationMatrix(degX)
    rotYMatrix = getYRotationMatrix(degY)
    rotZMatrix = getZRotationMatrix(degZ)

    rotationMatrix = rotXMatrix @ rotYMatrix @ rotZMatrix
    return rotationMatrix

# https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/lookat-function
# https://learnopengl.com/Getting-started/Camera
# I don't really know where the dot products came from--I think this function's math might be a bit wrong
# That would also explain why pitch doesn't work
# (but messing with it breaks it and yaw works enough so ¯\_(ツ)_/¯)
def getViewMatrix(pos, towards):
    alwaysUpCheat = [0, 1, 0] # this only works if the camera never goes 90deg up or down (gimbal lock)

    zForward = (towards - pos)[0:3]
    normVec(zForward)

    # These are not always perpendicular... (does that matter?)
    xRight = np.cross(zForward, alwaysUpCheat)
    normVec(xRight)

    yUp = np.cross(xRight, zForward)

    pos = pos[0:3] # This only applies to pos local (not a destructive op)
    
    # Not sure why pos needs to be negated here, but it just does!
    viewMatrix = np.array([
        [xRight[0], xRight[1], xRight[2], 0],
        [yUp[0], yUp[1], yUp[2], 0],
        [zForward[0], zForward[1], zForward[2], 0],
        [np.dot(xRight, -pos), np.dot(yUp, -pos), np.dot(zForward, -pos), 1]
    ])

    return viewMatrix

# for citations, see getProjectionMatrix
def projectPoly(poly: np.array, projectionMatrix):
    np.matmul(poly, projectionMatrix, poly)
    # Convert from homogenous projection to normalized projection
    for i, vertex in enumerate(poly):
        w = vertex[3]
        poly[i] /= w

def rotatePoly(rotationMatrix, poly: np.array, norms: np.array, hasNorms):
    np.matmul(poly, rotationMatrix, poly)
    if hasNorms:
        np.matmul(norms, rotationMatrix, norms)

# https://sites.google.com/site/3dprogramminginpython/
# ^Math sorta from there but then it didn't work and I had to intuitively figure it out anyway
# I'm probably overciting with this one tbh but you should know I saw the website and it has python source code
def toRasterSpace(poly: np.array, height, width):
    addOneMatrix = [1, 1, 0, 0]
    poly += addOneMatrix

    normalizeMatrix = [width/2, height/2, 1, 1]
    poly *= normalizeMatrix

# from https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-plane-and-ray-disk-intersection
def linePlaneIntersection(plane: np.array, planeNorm: np.array, P0, P1):
    rayDir = P1-P0
    t = np.dot((plane-P0), planeNorm)/(np.dot(rayDir, planeNorm))
    P = P0 + rayDir*t
    return P

# Concept from https://youtu.be/HXSuNxpCzdM?t=2378
def clipPolyOnNearPlane(poly: np.array, zNear = 2):
    zPlane, zPlaneNorm = [0, 0, zNear], [0, 0, 1]
    return clipPolyOnPlane(poly, zPlane, zPlaneNorm)

# This is from the video specifically--clipping in screen space against these "planes"
# pretty cool technique
def clipAllPolysOnScreenEdgePlanes(polysAndColors: np.array, height, width):
    bigPolysAndColors = []
    for poly, color in polysAndColors:
        result0, polys0 = clipPolyOnPlane(poly, [0, 0, 0], [0, 1, 0])
        result1, polys1 = clipPolyOnPlane(poly, [0, height, 0], [0, -1, 0])
        result2, polys2 = clipPolyOnPlane(poly, [0, 0, 0], [1, 0, 0])
        result3, polys3 = clipPolyOnPlane(poly, [width, 0, 0], [-1, 0, 0])
        
        bigPolys = polys0 + polys1 + polys2 + polys3
        
        for poly in bigPolys:
            bigPolysAndColors.append((poly, color))
             

    return True, bigPolysAndColors


# Returns tuple of format (isNewPolys, listOfNewPolys)
# isNewPolys == None -> don't do anything
# isNewPolys == False -> Delete entire polygon
# isNewPolys == True -> add listOfNewPolys to draw queue
# The current polygon is modified destructively, so there is no need to skip drawing
def clipPolyOnPlane(poly: np.array, plane: np.array, planeNorm: np.array): 
    # znear should probably be like 0.1 so it doesn't clip walls too near to the player, but that would require proper clipping on all planes
    newPolys = []
    clipped = []
    # for each vector in this polygon, if its z coordinate is too close to the camera, mark it for clipping
    for i, vec in enumerate(poly):
        dist = pointAndPlaneDist(vec, plane, planeNorm)
        if dist < 0:
            clipped.append(i)

    # This downwards is the concept taken from the video
    if len(clipped) == 0:
        return (None, newPolys)
    elif len(clipped) == 3:
        return (False, newPolys)

    notClipped = (set([0, 1, 2]) - set(clipped))

    # If one vert is too close to camera, make a quad (with a new polygon in newPolys)
    if len(clipped) == 1:
        vec0 = poly[clipped[0]]
        vec1 = poly[notClipped.pop()]
        vec2 = poly[notClipped.pop()]

        intersection1 = linePlaneIntersection(plane, planeNorm, vec0[0:3], vec1[0:3])
        intersection2 = linePlaneIntersection(plane, planeNorm, vec0[0:3], vec2[0:3])

        np.put(vec0, [0, 1, 2], intersection1) # Replace 0, 1, and 2 indices
        newPolys.append(np.array([vec0, vec2, np.append(intersection2, 1)]))
    # If two verts are too close to the camera, modify the current polygon
    elif len(clipped) == 2:
        vec0 = poly[clipped[0]]
        vec1 = poly[clipped[1]]
        vec2 = poly[notClipped.pop()]

        intersection1 = linePlaneIntersection(plane, planeNorm, vec0[0:3], vec2[0:3])
        intersection2 = linePlaneIntersection(plane, planeNorm, vec1[0:3], vec2[0:3])

        np.put(vec0, [0, 1, 2], intersection1) # Replace 0, 1, and 2 indices
        np.put(vec1, [0, 1, 2], intersection2) # Replace 0, 1, and 2 indices

    return (True, newPolys)

# https://www.youtube.com/watch?v=XgMWc6LumG4
def cull(avgNormal, poly, camPos):
    camRay = poly[0] - camPos
    camDiff = np.dot(avgNormal, camRay)
    if camDiff > 0:
        return True
    return False

# https://www.youtube.com/watch?v=XgMWc6LumG4
def flatLightingFactor(avgNormal, lightVector):
    return max(0.25, np.dot(avgNormal, lightVector))

# https://www.youtube.com/watch?v=XgMWc6LumG4
def paintersAlgorithm(polyAndColor):
    poly = polyAndColor[0]
    return sum(vector[2] for vector in poly)/3

# Version of the above that sorts by the closest values instead of midpoints.
def paintersAlgorithmMin(polyAndColor):
    poly = polyAndColor[0]
    return min(poly[:,2])

def vectorDist(vec0: np.array, vec1: np.array):
    subbed = vec1-vec0
    total = 0
    for term in subbed:
        total += term**2
    
    return math.sqrt(total)

# I know this is stackoverflow but this is a brilliantly simple answer don't @ me
# https://stackoverflow.com/questions/3860206/signed-distance-between-plane-and-point
def pointAndPlaneDist(point: np.array, plane: np.array, planeNorm: np.array):
    return np.dot(planeNorm, point[0:3]-plane[0:3])

# https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_plane#Restatement_using_linear_algebra
# https://tutorial.math.lamar.edu/classes/calciii/eqnsofplanes.aspx
def closestPointOnPlane(point: np.array, plane: np.array, planeNorm: np.array):
    planeScalar = sum(np.multiply(plane, planeNorm))
    pointOnPlane = (point*planeScalar)/(vectorMagnitude(point)**2)
    return pointOnPlane

# Checks all other meshes  
def rayIntersectsMeshFirst(mesh: Mesh, allMeshes, startPos, direction, rayLength):
    if not isMeshVaguelyInFront(mesh, startPos, direction):
        return False

    intersectsMesh, meshIntersectionPoint = rayIntersectsMesh(mesh, 
                                            startPos, direction, rayLength)
                
    if not intersectsMesh:
        return False

    intersectionDist = vectorDist(startPos, meshIntersectionPoint)

    for mesh in allMeshes:
            if not isMeshVaguelyInFront(mesh, startPos, direction):
                continue

            intersectsOther, otherIntersectionPoint = rayIntersectsMesh(mesh,
                                                    startPos, direction, rayLength)
            if intersectsOther and intersectionDist > vectorDist(startPos, otherIntersectionPoint):
                return False

    return True

def isMeshVaguelyInFront(mesh: Mesh, startPos, direction):
    avgVec = np.array([mesh.avgX, mesh.avgY, mesh.avgZ])
            
    # Get ray vector from mesh to camera
    ray = avgVec - startPos[0:3]
    normVec(ray)

    # Get similarity between camdir and ray
    similarity = np.dot(ray[0:3], direction[0:3])

    # If they aren't even close, skip
    return similarity > 0.6
    
# Returns tuple: (isIntersecting, intersectionPoint)
def rayIntersectsMesh(mesh: Mesh, startPos, direction, rayLength):
    # Check each polygon's plane for some reason
    for poly, norm in mesh.polys:
        # Find point of intersection with the plane
        intersection = linePlaneIntersection(poly[0], norm[0], startPos, direction*rayLength)
        
        # If intersection point is within the mesh, then its a hit!
        collides = pointCollision(mesh, intersection)
        if collides:
            return (True, intersection)

    return (False, None)

def meshCollidesWithOtherMeshes(mesh: Mesh, otherMeshes):
    for otherMesh in otherMeshes:
        if meshCollision(mesh, otherMesh):
            return True

    return False

def meshCollision(mesh0: Mesh, mesh1: Mesh):
    xCollides = mesh0.minX <= mesh1.minX <= mesh0.maxX or mesh0.minX <= mesh1.maxX <= mesh0.maxX
    yCollides = mesh0.minY <= mesh1.minY <= mesh0.maxY or mesh0.minY <= mesh1.maxY <= mesh0.maxY
    zCollides = mesh0.minZ <= mesh1.minZ <= mesh0.maxZ or mesh0.minZ <= mesh1.maxZ <= mesh0.maxZ
    return xCollides and yCollides and zCollides

def pointCollision(mesh: Mesh, pointVec: np.array, margin = 0):
    collides = (mesh.minX-margin <= pointVec[0] <= mesh.maxX+margin and 
                mesh.minY-margin <= pointVec[1] <= mesh.maxY+margin and 
                mesh.minZ-margin <= pointVec[2] <= mesh.maxZ+margin)

    return collides

# Used instead of built in np.linalg.norm for performance reasons
def normVec(vec: np.array):
    vec /= vectorMagnitude(vec)

def vectorMagnitude(vec: np.array):
    return math.sqrt(vec[0]**2+vec[1]**2+vec[2]**2)

def meshListToMesh(meshList):
    bigPolys = []
    for mesh in meshList:
        bigPolys.extend(mesh.polys)

    return Mesh(bigPolys, meshList[0].hasNormals, meshList[0].isTwoSided)