#Will find and remove staffs
#Will characterize notes and organize to write to xml

from staffLineDetectionRemoval import staffLineDetectionRemoval
from segmentationAndRecognition import segmentationAndRecognition

def musicSymbolRecognition(binaryImg):
    # DESCRIPTION: Takes the binary image and finds and recognizes all notes to be written to xml
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places)
    # RETURN: allMeasures: a list of lists of ConnectedComponent objects to be written to the xml

    newBinaryImg, staffLineRows = staffLineDetectionRemoval(binaryImg= binaryImg)
    allMeasures = segmentationAndRecognition(binaryImg=binaryImg, staffLines=staffLineRows)
    return allMeasures