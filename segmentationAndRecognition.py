#separates all notes through connected components
#recognizes notes
#takes in a binary image with no staff lines, and the positions of the staff lines
#returns a list of notes/symbols with position and type of note/symbol
import cv2
import copy
from connectedCompObj import ConnectedComponent

def segmentationAndRecognition(binaryImg, staffLines, lineDist):
    # DESCRIPTION: organizes the image into a list of connected components with some features detected
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places) with no staff lines
    #               staffLines: list of all the staff line indexes
    #               lineDist: the median distance between staff lines
    # RETURN: a list of all connected components with features detected
    connectedComponents = findConnectedComponents(binaryImg=binaryImg)
    #first connected component
    compNum = 1
    saveComponentList = []
    measuresToAddToCompList = []
    for comp in connectedComponents[1:]:
        if compNum in saveComponentList:
            comp.saveComponent(compNum=compNum)
        comp.templateMatch(compNum=compNum)
        if comp.typeName == None or comp.typeName == "note" or comp.typeName == "rest" or comp.typeName == "accent":
            if comp.typeName == "note" or comp.typeName == None:
                comp.findNoteheads(lineDist)
            comp.getStaff(staffLines=staffLines)
            comp.getPitches(staffLines=staffLines, distBetweenLines=lineDist)
        if comp.typeName == "measure bar":
            comp.getStaff(staffLines = staffLines)
            newMeasureBar = copy.deepcopy(comp)
            newMeasureBar.staff += 1
            measuresToAddToCompList.append(newMeasureBar)
        compNum += 1
    connectedComponents = connectedComponents + measuresToAddToCompList
    return connectedComponents

def findConnectedComponents(binaryImg):
    # DESCRIPTION: finds the connected components in the image
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places) with no staff lines
    # RETURN: a list of all connected components objects in the image
    connectivity = 8
    invertedImg = cv2.bitwise_not(binaryImg)
    nLabels, labels, stats, centroids = cv2.connectedComponentsWithStats(invertedImg, connectivity, cv2.CV_32S) #Citations [7,8]
    # nLabels is the number of connected components
    # stats is a matrix of the size of nLabels (one label for each component) with 5 items, left, top, width, height, area
    connectedComponents = []
    for label in range(nLabels):
        x0 = stats[label, cv2.CC_STAT_LEFT]
        y0 = stats[label, cv2.CC_STAT_TOP]
        x1 = stats[label, cv2.CC_STAT_LEFT] + stats[label, cv2.CC_STAT_WIDTH]
        y1 = stats[label, cv2.CC_STAT_TOP] + stats[label, cv2.CC_STAT_HEIGHT]
        minWidth = 10
        minHeight = 10
        #throw out any component too small
        if x1-x0 >= minWidth or y1-y0 >= minHeight:
            connectedComponents.append(ConnectedComponent(x0=x0, y0=y0, x1=x1, y1=y1, label=label, fullImg=binaryImg))
    return connectedComponents


###VISUALIZATION/DEBUGGING FUNCTIONS
###NOT VITAL TO PERFORMANCE
def drawConnectedComponentsAnno(binaryImg, connectedComponents):
    # DESCRIPTION: draws the image with the connectedComponents highlighted in green
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places) with no staff lines
    #               connectedComponents: a list of all the connected component objects
    # RETURN: None
    img = cv2.cvtColor(binaryImg, cv2.COLOR_GRAY2RGB)
    for cc in connectedComponents:
        img = cv2.rectangle(img, (cc.x0-5, cc.y0-5), (cc.x1+5, cc.y1+5), (0, 255, 0), 3)
    cv2.imshow('image', img)
    cv2.waitKey(0)