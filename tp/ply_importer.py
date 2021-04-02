from dataclasses import dataclass

import numpy as np

from threedee import Vector3D, Mesh

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
            headerInfo.vertexCount = int(line.split(" ")[-1])
        elif line.startswith("element face"):
            headerInfo.faceCount = int(line.split(" ")[-1])
        elif line.startswith("property float n"):
            headerInfo.hasNormals = True
        elif line == "end_header":
            headerInfo.endIndex = i
            return headerInfo

# Returns mesh
def readBody(headerInfo, fileAsString):
    contentStart = headerInfo.endIndex + 1
    facesStart = contentStart + headerInfo.vertexCount

    vectors = []
    polygons = []

    lines = fileAsString.splitlines()

    isNormal = False
    for lineNum in range(contentStart, facesStart):
        line = lines[lineNum]
        floats = [ float(word) for word in line.split(" ")]

        vertices = np.array(floats[0:3])
        vector = None
        if headerInfo.hasNormals and isNormal:
            normal = np.array(floats[3:6])
            vector = Vector3D(vertices[0],
                              vertices[1],
                              vertices[2],
                              normal[0],
                              normal[1],
                              normal[2])
        else:
            vector = Vector3D(vertices[0],
                    vertices[1],
                    vertices[2])

        vectors.append(vector)

        isNormal = not isNormal

    for lineNum in range(facesStart, len(lines)):
        line = lines[lineNum]
        ints = [ int(word) for word in line.split(" ")]
        if ints[0] != 3:
            raise Exception("Face in file has more than 3 vertices!")

        poly = [vectors[ints[1]], 
                 vectors[ints[2]], 
                 vectors[ints[3]]]

        polygons.append(poly)

    return Mesh(polygons)



def importPly(path):
    fileAsString = readFile(path)

    headerInfo = readHeader(fileAsString)

    mesh = readBody(headerInfo, fileAsString)

    return mesh



        