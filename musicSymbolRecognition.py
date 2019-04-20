#Will find and remove staffs
#Will characterize notes and organize to write to xml

from staffLineDetectionRemoval import staffLineDetectionRemoval
from segmentationAndRecognition import segmentationAndRecognition
from organizeComps import organizeComponents
import math

def musicSymbolRecognition(binaryImg, divisions):
    # DESCRIPTION: Takes the binary image and finds and recognizes all notes to be written to xml
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places)
    # RETURN: allMeasures: a list of lists of ConnectedComponent objects to be written to the xml

    newBinaryImg, staffLineRows = staffLineDetectionRemoval(binaryImg= binaryImg)
    lineDist = getMedianLineDist(staffLines=staffLineRows)
    allComponents, timeSig, divisions = segmentationAndRecognition(binaryImg=binaryImg, staffLines=staffLineRows, lineDist=lineDist, divisions=divisions)
    allMeasures, keySig = organizeComponents(binaryImg=binaryImg, connectedComponents=allComponents, lineDist=lineDist)
    return allMeasures, timeSig, divisions, keySig


def getMedianLineDist(staffLines):
    # DESCRIPTION: gets the median difference between an of the staff line rows
    # PARAMETERS: staffLines: 2D List representing all the staff line locations on the page
    # RETURN: the median distance between any two staff lines
    singleYLines = []
    for line in staffLines:
        if len(line)%2 == 1:
            singleYLines.append(line[math.floor(len(line)/2)])
        else:
            singleYLines.append(sum(line)/len(line))
    distances = []
    for i in range(1, len(singleYLines)):
        distances.append(singleYLines[i]-singleYLines[i-1])
    return sorted(distances)[int(len(distances)/2)]