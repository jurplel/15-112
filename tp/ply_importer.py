from dataclasses import dataclass

import numpy as np

from threedee import Mesh

# From here: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()


# Imports PLY 3d model files
# Export from Blender in ASCII mode with everything but normals unchecked
# http://learnwebgl.brown37.net/modelers/ply_data_format.html

@dataclass
class HeaderInfo:
    vertexCount: int = -1
    faceCount: int = -1
    hasNormals: bool = False
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
    normalPolygons = []

    lines = fileAsString.splitlines()

    for lineNum in range(contentStart, facesStart):
        line = lines[lineNum]
        points = np.array([ float(word) for word in line.split()])
        points = np.insert(points, 3, 1)
        points = np.append(points, 0) # 0 for normal's w

        vertices.append(points[0:4])
        if headerInfo.hasNormals:
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

    return Mesh(np.array(polygons), headerInfo.hasNormals)



def importPly(path):
    fileAsString = readFile(path)

    headerInfo = readHeader(fileAsString)

    mesh = readBody(headerInfo, fileAsString)

    print(f"Loaded {path} with {len(mesh.polys)} polygons")
    return mesh



        