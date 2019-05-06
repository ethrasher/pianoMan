#separates all notes through connected components
#recognizes notes
#takes in a binary image with no staff lines, and the positions of the staff lines
#returns a list of notes/symbols with position and type of note/symbol
import cv2
import numpy as np
import copy
import time
from connectedCompObj import ConnectedComponent, NoteComponent, RestComponent, MeasureBarComponent, AccentComponent, OtherComponent

def segmentationAndRecognition(binaryImg, staffLines, lineDist, divisions):
    # DESCRIPTION: organizes the image into a list of connected components with some features detected
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places) with no staff lines
    #               staffLines: list of all the staff line indexes
    #               lineDist: the median distance between staff lines
    # RETURN: a list of all connected components with features detected
    fullStartTime = time.time()
    connectedComponents = findConnectedComponents(binaryImg=binaryImg)
    saveComponentList = []
    showComponentList = []
    templateObjList = []
    for comp in connectedComponents:
        #comp.saveComponent(False)
        compNum = comp.compNum
        if compNum in saveComponentList:
            pass
            comp.saveComponent()
        if compNum in showComponentList:
            pass
            comp.drawComponent()
            comp.drawComponentOnCanvas()
            cv2.waitKey(0)
        startTime = time.time()
        templateObj = comp.templateMatch(staffLines=staffLines, lineDist = lineDist)
        endTime = time.time()
        print("Template match comp %d time: "%compNum, endTime-startTime)

        if type(templateObj) == tuple or type(templateObj) == list:
            for obj in templateObj:
                templateObjList.append(obj)
        else:
            templateObjList.append(templateObj)

    timeSig = None
    smallestNoteType = None
    measuresToAddToTemplateList = []
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
    templateObjList = templateObjList + measuresToAddToTemplateList
    divisions = getDivisions(smallestNoteType=smallestNoteType, divisions=divisions)
    fullEndTime = time.time()
    print("segmentationRecognition Time: ", fullEndTime-fullStartTime)
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
    for label in range(1, nLabels):
        #Ignore first CC since that is the whole image
        x0 = stats[label, cv2.CC_STAT_LEFT]
        y0 = stats[label, cv2.CC_STAT_TOP]
        x1 = stats[label, cv2.CC_STAT_LEFT] + stats[label, cv2.CC_STAT_WIDTH]
        y1 = stats[label, cv2.CC_STAT_TOP] + stats[label, cv2.CC_STAT_HEIGHT]
        minWidth = 10
        minHeight = 10
        #throw out any component too small
        if x1-x0 >= minWidth or y1-y0 >= minHeight:
            #origComponentImg = np.copy(binaryImg[y0:y1, x0:x1])
            componentImg = np.copy(labels[y0:y1, x0:x1])
            filterer = lambda x: np.uint8(0) if (x==label) else np.uint8(255)
            componentImg = np.vectorize(filterer)(componentImg)
            cc = ConnectedComponent(x0=x0, y0=y0, x1=x1, y1=y1, label=label, componentImg=componentImg, binaryImg=np.copy(binaryImg), compNum=label)
            connectedComponents.append(cc)
    return connectedComponents

def getSmallerNoteType(origNote, compareNote):
    # DESCRIPTION: gets the smallest type of note in the page
    # PARAMETERS: origNote: string (whole, half, ...) representing the smallest note found before in the page
    #               compareNote: the next note in the page, which may be smaller
    # RETURN: string representing the duration of the now smallest object in the page (whole, half, ...)
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
    elif origNote == "16th":
        origDuration = 1
    else:
        raise Exception("OrigNote type not whole, half, quareter, eighth, 16th")

    if compareNote == "whole":
        compareDuration = 5
    elif compareNote == "half":
        compareDuration = 4
    elif compareNote == "quarter":
        compareDuration = 3
    elif compareNote == "eighth":
        compareDuration = 2
    elif compareNote == "16th":
        compareDuration = 1
    else:
        raise Exception("CompareNote type not whole, half, quarter, eighth, 16th")

    if compareDuration <= origDuration:
        return compareNote
    else:
        return origNote

def getDivisions(smallestNoteType, divisions):
    # DESCRIPTION: gets the division number based on the smallest note type in the song
    # PARAMETERS: smallestNoteType: string (whole, half, ...) representing the smallest note found before in the page
    # RETURN: integer representing the duration value to go into the xml
    if divisions == None:
        if smallestNoteType == "whole":
            return .25
        elif smallestNoteType == "half":
            return .5
        elif smallestNoteType == "quarter":
            return 1
        elif smallestNoteType == "eighth":
            return 2
        elif smallestNoteType == "16th":
            return 4
        else:
            raise Exception("smallestNoteType is %s not whole, half, quarter, eighth, 16th"%(str(smallestNoteType)))
    else:
        if smallestNoteType == "whole":
            return max(divisions, .25)
        elif smallestNoteType == "half":
            return max(divisions, .5)
        elif smallestNoteType == "quarter":
            return max(divisions, 1)
        elif smallestNoteType == "eighth":
            return max(divisions, 2)
        elif smallestNoteType == "16th":
            return max(divisions, 4)
        else:
            raise Exception("smallestNoteType is %s not whole, half, quarter, eighth, 16th"%(str(smallestNoteType)))



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