from dataclasses import dataclass

import numpy as np

from ddd import Mesh

# From here: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

# Imports PLY 3d model files
# Works with exports from Blender in ASCII mode (Y up, Z forward for this game)
# Model must be split into triangles (Modeling tab, edit mode, press A to select all, Ctrl+T to triangulate)
# http://learnwebgl.brown37.net/modelers/ply_data_format.html

@dataclass
class HeaderInfo:
    vertexCount: int = -1
    faceCount: int = -1
    hasNormals: bool = False
    hasUV: bool = False
    endIndex: int = -1

# Returns HeaderInfo dataclass
def readHeader(fileAsString):
    if not fileAsString.startswith("ply"):
        raise Exception("This is not a PLY file!")
    
    headerInfo = HeaderInfo()
    for i, line in enumerate(fileAsString.splitlines()):
        if line.startswith("element vertex"):
            headerInfo.vertexCount = int(line.split()[-1])
        elif line.startswith("element face"):
            headerInfo.faceCount = int(line.split()[-1])
        elif line.startswith("property float n"):
            headerInfo.hasNormals = True
        elif line.startswith("property float s") or line.startswith("propertly float u"):
            headerInfo.hasUV = True
        elif line == "end_header":
            headerInfo.endIndex = i
            return headerInfo

# Returns mesh
def readBody(headerInfo, fileAsString):
    contentStart = headerInfo.endIndex + 1
    facesStart = contentStart + headerInfo.vertexCount

    vertices = []
    normals = []
    polygons = []

    lines = fileAsString.splitlines()

    for lineNum in range(contentStart, facesStart):
        line = lines[lineNum]
        points = np.array([ float(word) for word in line.split()])
        points = np.insert(points, 3, 1)

        vertices.append(points[0:4])
        if headerInfo.hasNormals:
            points = np.insert(points, 7, 0) # 0 for normal's w
            normals.append(points[4:8])

    for lineNum in range(facesStart, len(lines)):
        line = lines[lineNum]
        ints = [ int(word) for word in line.split()]
        if ints[0] != 3:
            raise Exception("Face in file has more than 3 vertices!")

        poly = np.array([vertices[ints[1]], 
                 vertices[ints[2]], 
                 vertices[ints[3]]])
        normPoly = None
        if headerInfo.hasNormals:
            normPoly = np.array([normals[ints[1]], 
                normals[ints[2]], 
                normals[ints[3]]])
            
        polygons.append((poly, normPoly))

    return Mesh(polygons, headerInfo.hasNormals)



def importPly(path):
    fileAsString = readFile(path)

    headerInfo = readHeader(fileAsString)

    mesh = readBody(headerInfo, fileAsString)

    print(f"Loaded {path} with {len(mesh.polys)} polygons")
    return mesh



        