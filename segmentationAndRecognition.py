#separates all notes through connected components
#recognizes notes
#takes in a binary image with no staff lines, and the positions of the staff lines
#returns a list of notes/symbols with position and type of note/symbol
import cv2
import numpy as np
import copy
from connectedCompObj import ConnectedComponent, NoteComponent, RestComponent, MeasureBarComponent, AccentComponent, OtherComponent

def segmentationAndRecognition(binaryImg, staffLines, lineDist):
    # DESCRIPTION: organizes the image into a list of connected components with some features detected
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places) with no staff lines
    #               staffLines: list of all the staff line indexes
    #               lineDist: the median distance between staff lines
    # RETURN: a list of all connected components with features detected
    connectedComponents = findConnectedComponents(binaryImg=binaryImg)
    #first connected component
    compNum = 0
    saveComponentList = []
    measuresToAddToTemplateList = []
    templateObjList = []
    timeSig = None
    smallestNoteType = None
    for comp in connectedComponents[1:]:
        if compNum in saveComponentList:
            comp.saveComponent(compNum=compNum)
        templateObj = comp.templateMatch(staffLines=staffLines, lineDist = lineDist, compNum=compNum)
        templateObjList.append(templateObj)
    for templateObj in templateObjList:
        if isinstance(templateObj, NoteComponent):
            smallestNoteType = getSmallerNoteType(smallestNoteType, templateObj.durationName)
        #ignore rest and accent case. They are already done
        if isinstance(templateObj, MeasureBarComponent):
            newMeasureBar = copy.deepcopy(templateObj)
            newMeasureBar.staff += 1
            measuresToAddToTemplateList.append(newMeasureBar)
        if isinstance(templateObj, OtherComponent):
            if templateObj.typeName == "time signature":
                timeSig = templateObj.getTimeSignature()
        compNum += 1
    templateObjList = templateObjList + measuresToAddToTemplateList
    divisions = getDivisions(smallestNoteType=smallestNoteType)
    return templateObjList, timeSig, divisions

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
            componentImg = np.copy(binaryImg[y0:y1, x0:x1])
            connectedComponents.append(ConnectedComponent(x0=x0, y0=y0, x1=x1, y1=y1, label=label, componentImg=componentImg))
    return connectedComponents

def getSmallerNoteType(origNote, compareNote):
    if origNote == None:
        return compareNote
    if origNote == "whole":
        origDuration = 5
    elif origNote == "half":
        origDuration = 4
    elif origNote == "quarter":
        origDuration = 3
    elif origNote == "eighth":
        origDuration = 2
    elif origNote == "sixteenth":
        origDuration = 1
    else:
        raise Exception("OrigNote type not whole, half, quareter, eighth, sixteenth")

    if compareNote == "whole":
        compareDuration = 5
    elif compareNote == "half":
        compareDuration = 4
    elif compareNote == "quarter":
        compareDuration = 3
    elif compareNote == "eighth":
        compareDuration = 2
    elif compareNote == "sixteenth":
        compareDuration = 1
    else:
        raise Exception("CompareNote type not whole, half, quarter, eighth, sixteenth")

    if compareDuration <= origDuration:
        return compareNote
    else:
        return origNote

def getDivisions(smallestNoteType):
    if smallestNoteType == "whole":
        return .25
    elif smallestNoteType == "half":
        return .5
    elif smallestNoteType == "quarter":
        return 1
    elif smallestNoteType == "eighth":
        return 2
    elif smallestNoteType == "sixteenth":
        return 4
    else:
        raise Exception("smallestNoteType not whole, half, quarter, eighth, sixteenth")



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