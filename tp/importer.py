from dataclasses import dataclass

import numpy as np

import threedee

# From here: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()


# Imports basic Stanford format PLY 3d model files
# Export from Blender in ASCII mode with everything unchecked
# http://learnwebgl.brown37.net/modelers/ply_data_format.html

@dataclass
class HeaderInfo:
    vertexCount: int = -1
    faceCount: int = -1
    endIndex: int = -1

# Returns HeaderInfo dataclass
def readHeader(fileAsString):
    headerInfo = HeaderInfo()
    for i, line in enumerate(fileAsString.splitlines()):
        if line.startswith("element vertex"):
            headerInfo.vertexCount = int(line.split(" ")[-1])
        elif line.startswith("element face"):
            headerInfo.faceCount = int(line.split(" ")[-1])
        elif line == "end_header":
            headerInfo.endIndex = i
            return headerInfo

# Returns mesh
def readBody(headerInfo, fileAsString):
    contentStart = headerInfo.endIndex + 1
    facesStart = contentStart + headerInfo.vertexCount

    vertices = []
    polygons = []

    lines = fileAsString.splitlines()

    for lineNum in range(contentStart, facesStart):
        line = lines[lineNum]
        floats = [ float(word) for word in line.split(" ")]
        vector = np.array(floats)
        vertices.append(vector)

    for lineNum in range(facesStart, len(lines)):
        line = lines[lineNum]
        ints = [ int(word) for word in line.split(" ")]
        if ints[0] != 3:
            raise Exception("Face in file has more than 3 vertices!")

        poly = [vertices[ints[1]], 
                 vertices[ints[2]], 
                 vertices[ints[3]]]

        polygons.append(poly)

    return threedee.Mesh(polygons)



def importPly(path):
    fileAsString = readFile(path)

    headerInfo = readHeader(fileAsString)

    mesh = readBody(headerInfo, fileAsString)

    return mesh



        