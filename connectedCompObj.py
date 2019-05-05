#An Object to keep track of all the connected components
#Eventually will add more here like noteheads and pitch
import cv2
import math
import os
import numpy as np

class ConnectedComponent(object):
    def __init__(self, x0, y0, x1, y1, label, componentImg, binaryImg, compNum):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.label = label
        self.componentImg = componentImg
        self.fullBinaryImg = binaryImg
        self.compNum = compNum

    def drawComponent(self, windowName="componentImg"):
        # DESCRIPTION: draws the component in a separate image
        # PARAMETERS: windowName: string of the name for the window for openCV
        # RETURN: None
        cv2.imshow(windowName, self.componentImg)

    def saveComponent(self, saveCanvas=False):
        # DESCRIPTION: saves the image of the component into the template folder so it will match the next time
        # PARAMETERS: compNum: the number of this component
        # RETURN: None
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        compPath = scriptPath + '/templates/aaa_unknownCompImages/component%d.jpg'%(self.compNum)
        cv2.imwrite(compPath, self.componentImg)
        if saveCanvas:
            canvasPath = scriptPath + '/templates/aaa_unknownCompImages/canvas%d.jpg'%(self.compNum)
            img = cv2.cvtColor(self.fullBinaryImg, cv2.COLOR_GRAY2RGB)
            img = cv2.rectangle(img, (self.x0 - 5, self.y0 - 5), (self.x1 + 5, self.y1 + 5), (0, 0, 255), 6)
            cv2.imwrite(canvasPath, img)
            return compPath, canvasPath
        return compPath


    def drawComponentOnCanvas(self, windowName='componentOnCanvas'):
        # DESCRIPTION: draws the component highlighted in a square box on the full page image
        # PARAMETERS: binaryImg: the full image of the page
        #               windowName: string of the name for the window for openCV
        # RETURN: None
        img = cv2.cvtColor(self.fullBinaryImg, cv2.COLOR_GRAY2RGB)
        img = cv2.rectangle(img, (self.x0 - 5, self.y0 - 5), (self.x1 + 5, self.y1 + 5), (0, 0, 255), 6)
        cv2.imshow(windowName, img)

    def templateMatch(self, staffLines, lineDist):
        # DESCRIPTION: matches the component image to all the templates in the path to see if there is a match
        # PARAMETERS: staffLines: 2D list of all the staff lines in the image
        #               lineDist: the median distance between any 2 staff lines
        #               compNum: the number of this component
        # RETURN: a new object for which the component matched. None if it could not find a match
        allTemplatesPath = scriptPath = os.path.dirname(os.path.realpath(__file__)) + "/templates"
        bestTemplatePath = None
        bestMatch = 0.8 # need to be over 80% to be considered a match anyway
        allSubFiles = ConnectedComponent.getAllSubFolders(allTemplatesPath)
        compImgWHRatio = self.componentImg.shape[0]/self.componentImg.shape[1]
        for templatePath in allSubFiles:
            templateImg = cv2.imread(templatePath, 0)  # Load an color image in grayscale of the page of music
            ret, templateImg = cv2.threshold(templateImg, 230, 255, cv2.THRESH_BINARY)
            #check if porportions ratio is roughly the same
            templateImgWHRatio = templateImg.shape[0]/templateImg.shape[1]
            ratioThreshold = .25
            if (abs(1-compImgWHRatio/templateImgWHRatio) > ratioThreshold):
                continue
            #check pixel differences when resized
            templateImg = cv2.resize(templateImg, (self.componentImg.shape[1], self.componentImg.shape[0]))
            # find all differences in pixel values between the two images
            diffImg = np.logical_xor(self.componentImg, templateImg) #Citations: [12]
            # find counts of all True values (differences)
            unique, counts = np.unique(diffImg, return_counts=True) #Citations: [13]
            sameCounts = dict(zip(unique, counts)).get(False, 0)
            totalPixels = self.componentImg.shape[0] * self.componentImg.shape[1]
            matchValue = sameCounts/totalPixels
            # check if this template is a better match than what we have seen previously
            if matchValue > bestMatch:
                bestMatch = matchValue
                bestTemplatePath = templatePath
                if (abs(matchValue - 1) < 10**-9):
                    break
        # update attributes based on which template matches

        if (bestTemplatePath == None):
            # could not find a template to match
            templatePath, canvasPath = self.saveComponent(True)
            unknownComp = UnknownComponent(self.x0, self.y0, self.x1, self.y1, self.label, self.componentImg, self.fullBinaryImg, self.compNum, templatePath, canvasPath)
            return unknownComp
        lastFolder = bestTemplatePath.split("/")[-2]
        if (lastFolder == "aaa_unknownCompImages"):
            # don't need to save it again
            # get the canvas path
            canvasName = bestTemplatePath.split("/")[-1]
            canvasName = "canvas"+canvasName[9:]
            canvasPath = (bestTemplatePath.split("/")[:-1])
            canvasPath.append(canvasName)
            canvasPath = "/".join(canvasPath)

            unknownComp = UnknownComponent(self.x0, self.y0, self.x1, self.y1, self.label, self.componentImg,
                                           self.fullBinaryImg, self.compNum, bestTemplatePath, canvasPath)
            return unknownComp
        else:
            templatePath = bestTemplatePath.split("templates/")[1]
            return self.makeTemplateObject(bestTemplatePath, staffLines, lineDist)

    def makeTemplateObject(self, templatePath, staffLines, lineDist):
        # DESCRIPTION: creates the new object based on which template it matched to
        # PARAMETERS: templatePath: string file path to the closest matched template
        #               staffLines: 2D list representing all the staffLine locations
        #               lineDist: median line distance between any two staff lines
        #               compNum: the number for this component
        # RETURN: None
        if templatePath.find("aaa_note_whole") >= 0:
            # it is a whole note
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="whole", stem=None, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=self.compNum)
        elif templatePath.find("aaa_note_half") >= 0:
            # it is a half note
            stemDirString = templatePath.split("/")[-2]
            if stemDirString == "stemUp": stem = "up"
            elif stemDirString == "stemDown": stem = "down"
            else: raise Exception("Could not get stem for half note, compNum:" + str(self.compNum))
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="half", stem=stem, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=self.compNum)
        elif templatePath.find("aaa_note_quarter") >= 0:
            # it is a quarter note
            stemDirString = templatePath.split("/")[-2]
            if stemDirString == "stemUp":
                stem = "up"
            elif stemDirString == "stemDown":
                stem = "down"
            else:
                raise Exception("Could not get stem for quarter note, compNum:" + str(self.compNum))
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="quarter", stem=stem, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=self.compNum)
        elif templatePath.find("aaa_note_eighth") >= 0:
            # it is an eighth note
            stemDirString = templatePath.split("/")[-2]
            if stemDirString == "stemUp":
                stem = "up"
            elif stemDirString == "stemDown":
                stem = "down"
            else:
                raise Exception("Could not get stem for half note, compNum:" + str(self.compNum))
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="eighth", stem=stem, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=self.compNum)
        elif templatePath.find("aaa_note_sixteenth") >= 0:
            stemDirString = templatePath.split("/")[-2]
            if stemDirString == "stemUp":
                stem = "up"
            elif stemDirString == "stemDown":
                stem = "down"
            else:
                raise Exception("Could not get stem for half note, compNum:" + str(self.compNum))
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="sixteenth", stem=stem, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=self.compNum)
        elif templatePath.find("aaa_note_chord") >= 0:
            # it is a multi-note chord
            durationName = (templatePath.split("/")[-3]).split("_")[1]
            numberOfPitches = int(templatePath.split("/")[-2])
            stemDirString = templatePath.split("/")[-4]
            if stemDirString == "stemUp":
                stem = "up"
            elif stemDirString == "stemDown":
                stem = "down"
            else:
                raise Exception("Could not get stem for half note, compNum:" + str(self.compNum))
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration=durationName, stem=stem, numPitches=numberOfPitches,
                                 staffLines=staffLines, lineDist=lineDist, compNum=self.compNum)

        elif templatePath.find("aaa_note_connected") >= 0:
            # it is a series of connected notes
            typeName = "note"
            subTypeName = "connected"
            stemDirString = templatePath.split("/")[-3]
            if stemDirString == "stemUp":
                stem = "up"
            elif stemDirString == "stemDown":
                stem = "down"
            else:
                raise Exception("Could not get stem for half note, compNum:" + str(self.compNum))
            numberOfStems = len(templatePath.split("/")[-2])
            numberOfPitches = [int(templatePath.split("/")[-2][i]) for i in range(numberOfStems)]

            # need the new image components for each stem, duration for each stem, numPitches on each stem
            durationName = None
            stemLocations = ConnectedComponent.getLocationOfStems(self.componentImg, numberOfStems)
            midpointsBetweenStems = ConnectedComponent.getLocationOfMidPoints(stemLocations, numberOfStems)
            allNotes = []
            for i in range(numberOfStems):
                if i == 0:
                    x0 = 0
                    fullImgX0 = self.x0
                else:
                    x0 = midpointsBetweenStems[i-1]
                    fullImgX0 = midpointsBetweenStems[i-1] + self.x0
                if i == (numberOfStems-1):
                    x1 = self.componentImg.shape[1]
                    fullImgX1 = self.x1
                else:
                    x1 = midpointsBetweenStems[i]
                    fullImgX1 = midpointsBetweenStems[i] + self.x0
                fullImgY0 = self.y0
                fullImgY1 = self.y1
                componentImg = np.copy(self.componentImg[:, x0:x1])
                durationName = "eighth"
                #durationName = NoteComponent.getDurationOfConnectedNote(componentImg, i, numberOfStems)
                if i == 0:
                    beam = "begin"
                elif i == numberOfStems-1:
                    beam = "end"
                else:
                    beam = "continue"

                #TODO: NEED TO FIND DURATION PROPERLY
                newNote = self.findConnectedNoteAttributes(x0=fullImgX0, y0=fullImgY0, x1=fullImgX1, y1=fullImgY1,
                                 componentImg=componentImg, stem=stem, numPitches=numberOfPitches[i],
                                 staffLines=staffLines, lineDist=lineDist, compNum=self.compNum+(1/numberOfStems), beam=beam)
                #newNote = NoteComponent(x0=fullImgX0, y0=fullImgY0, x1=fullImgX1, y1=fullImgY1, label=self.label,
                #                 componentImg=componentImg, binaryImg=self.fullBinaryImg, duration=durationName, stem=stem, numPitches=numberOfPitches[i],
                #                 staffLines=staffLines, lineDist=lineDist, compNum=self.compNum+(1/numberOfStems), beam=beam)
                allNotes.append(newNote)
            return allNotes

        elif templatePath.find("aaa_rest_whole") >= 0:
            # it is a whole rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="whole", staffLines=staffLines,
                                 compNum=self.compNum)
        elif templatePath.find("aaa_rest_half") >= 0:
            # it is a half rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="half", staffLines=staffLines,
                                 compNum=self.compNum)
        elif templatePath.find("aaa_rest_quarter") >= 0:
            # it is a quarter rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="quarter", staffLines=staffLines,
                                 compNum=self.compNum)
        elif templatePath.find("aaa_rest_eighth") >= 0:
            # it is an eighth rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="eighth", staffLines=staffLines,
                                 compNum=self.compNum)
        elif templatePath.find("aaa_rest_sixteenth") >= 0:
            # it is a sixteenth rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, binaryImg=self.fullBinaryImg, duration="sixteenth", staffLines=staffLines,
                                 compNum=self.compNum)


        elif templatePath.find("aaa_measure_bar") >= 0:
            # it is a measure_barx0, y0, x1, y1, label, componentImg, staffLines, compNum
            return MeasureBarComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label, componentImg=self.componentImg, binaryImg=self.fullBinaryImg, staffLines=staffLines, compNum=self.compNum)


        elif templatePath.find("aaa_accent") >= 0:
            #it is an accent
            subType = templatePath.split("/")[-2]
            return AccentComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label, componentImg=self.componentImg, binaryImg=self.fullBinaryImg, subType=subType, staffLines=staffLines, compNum=self.compNum)


        elif templatePath.find("aaa_clef_treble") >= 0:
            # it is a treble_clef
            type = "clef"
            subType = "treble"
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, binaryImg=self.fullBinaryImg, type=type, subType=subType, compNum=self.compNum)
        elif templatePath.find("aaa_clef_base") >= 0:
            # it is a base_clef
            type = "clef"
            subType = "base"
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, binaryImg=self.fullBinaryImg, type=type, subType=subType, compNum=self.compNum)
        elif templatePath.find("aaa_timeSignature") >= 0:
            # it is a timeSig
            type = "time signature"
            subType = templatePath.split("/")[-2]
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, binaryImg=self.fullBinaryImg, type=type, subType=subType, compNum=self.compNum)
        elif templatePath.find("aaa_staveSwirl") >= 0:
            # it is a stave Swirl
            type = "stave swirl"
            subType = None
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, binaryImg=self.fullBinaryImg, type=type, subType=subType, compNum=self.compNum)
        elif templatePath.find("aaa_alphaNum") >= 0:
            # it is an alpha-numeric character
            type = "alphaNum"
            subType = None
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, binaryImg=self.fullBinaryImg, type=type, subType=subType, compNum=self.compNum)

    @staticmethod
    def getLocationOfStems(image, numOfStems):
        transposedImage = np.transpose(image)
        amountColBlack = np.zeros(transposedImage.shape[0])
        # i is the row, j is the col
        for i in range(transposedImage.shape[0]):
            unique, counts = np.unique(transposedImage[i], return_counts=True)  # Citations [13]
            blackCounts = dict(zip(unique, counts)).get(0, 0)
            amountColBlack[i] += blackCounts
            if i > 0:
                amountColBlack[i - 1] += blackCounts
            if i < transposedImage.shape[0] - 1:
                amountColBlack[i + 1] += blackCounts
        colBlackIndexSort = np.argsort(amountColBlack)[::-1]
        stemLocations = []
        colIndexCheck = 0
        stemDistThreshold = transposedImage.shape[0] // (numOfStems + 2)
        while len(stemLocations) < numOfStems:
            # take the cols with the most black that are far enough away from each other
            indexToAdd = colBlackIndexSort[colIndexCheck]
            appendIndex = True
            for prevIndex in stemLocations:
                if abs(prevIndex - indexToAdd) < stemDistThreshold:
                    appendIndex = False
                    break
            if appendIndex:
                stemLocations.append(indexToAdd)
            colIndexCheck += 1
        stemLocations.sort()
        return stemLocations

    @staticmethod
    def getLocationOfMidPoints(stemLocations, numOfStems):
        stemMidPoints = []
        for i in range(numOfStems-1):
            stemMidPoints.append(int((stemLocations[i]+stemLocations[i+1])//2))
        return stemMidPoints

    def findConnectedNoteAttributes(self, x0, y0, x1, y1, componentImg, stem, numPitches, staffLines, lineDist, compNum, beam):
        # step 1: find midpoints between notes -> already done
        # step 2: get separate components -> already done
        # step 3: find stem in image (start and stop)
        stemLocation = ConnectedComponent.getLocationOfStems(componentImg, 1)[0]

        stemTop = None
        stemBottom = None
        for row in range(componentImg.shape[0]):
            if componentImg[row][stemLocation] == 0 and stemTop == None:
                stemTop = row
            elif componentImg[row][stemLocation] == 255 and stemTop != None and stemBottom == None:
                stemBottom = row-1
                break
        if stemBottom == None:
            # the stem reaches the bottom of the image
            stemBottom = componentImg.shape[0]
        # step 4: include thershold pixels above and below it to make sure to include everything
        includeThresholdPixels = 15
        topRow = max(0, stemTop-includeThresholdPixels)
        bottomRow = min(componentImg.shape[0], stemBottom+includeThresholdPixels)
        componentImg = np.copy(componentImg[topRow:bottomRow, 0:componentImg.shape[1]])
        y0 += topRow
        y1 = y1 - componentImg.shape[0]-bottomRow
        # step 5: using stem direction look at top or bottom half of image (half with noteheads)
        if stem == "up":
            # want bottom half
            noteheadHalfImage = np.copy(componentImg[componentImg.shape[0]//2:, 0:componentImg.shape[1]])
        elif stem == "down":
            noteheadHalfImage = np.copy(componentImg[:componentImg.shape[0]//2, 0:componentImg.shape[1]])
        else:
            raise Exception("stem not up or down")
        # step 6: find first left and right black pixel
        transposedNoteheadImage = np.transpose(noteheadHalfImage)
        leftBlackCol = None
        rightBlackCol = None
        for i in range(transposedNoteheadImage.shape[0]):
            unique, counts = np.unique(transposedNoteheadImage[i], return_counts=True)  # Citations [13]
            blackCounts = dict(zip(unique, counts)).get(0, 0)
            if blackCounts > 0 and leftBlackCol == None:
                leftBlackCol = i
            elif blackCounts == 0 and rightBlackCol == None and leftBlackCol != None:
                rightBlackCol = i-1
        if rightBlackCol == None:
            rightBlackCol = transposedNoteheadImage.shape[0]-1
        # step 7: cut down image using new left and right bounding box
        leftRightPixelThreshold = 8
        leftBlackCol = max(0, leftBlackCol-leftRightPixelThreshold)
        rightBlackCol = min(componentImg.shape[1], rightBlackCol+leftRightPixelThreshold)
        componentImg = np.copy(componentImg[:, leftBlackCol:rightBlackCol+1])
        x0 += leftBlackCol
        x1 = x1 - componentImg.shape[1] - rightBlackCol+1
        # step 8: using top half of image use 5 pixels left and 5 pixels right to find duration
        if stem == "up":
            # want top half
            beamHalfImage = np.copy(componentImg[:componentImg.shape[0]//2, :])
        elif stem == "down":
            beamHalfImage = np.copy(componentImg[componentImg.shape[0]//2:, :])
        else:
            raise Exception("stem not up or down")
        if beam == "begin":
            duration = ConnectedComponent.getDurationOfConnectedNote(beamHalfImage, 0, 2)
        elif beam == "end":
            duration = ConnectedComponent.getDurationOfConnectedNote(beamHalfImage, 1, 2)
        elif beam == "continue":
            duration = ConnectedComponent.getDurationOfConnectedNote(beamHalfImage, 1, 3)
        else:
            raise Exception("beam is not begin end or continue")
        print("duration: ", duration)
        newNote = NoteComponent(x0=x0, y0=y0, x1=x1, y1=y1, label=self.label,
                        componentImg=componentImg, binaryImg=self.fullBinaryImg, duration=duration, stem=stem, numPitches=numPitches,
                        staffLines=staffLines, lineDist=lineDist, compNum=compNum, beam=beam)
        return newNote

    @staticmethod
    def getDurationOfConnectedNote(image, noteNum, totalNum):
        transposedImage = np.transpose(image)
        rightEdge = transposedImage[transposedImage.shape[0]-1]
        leftEdge = transposedImage[0]
        leftEdgeNumBars = 0
        rightEdgeNumBars = 0
        lastSeenColor = 255
        if noteNum > 0:
            print("not first note")
            # not the first note in connected notes
            # need to find left edge bars
            for i in range(leftEdge.shape[0]):
                curColor = leftEdge[i]
                if lastSeenColor == 255 and curColor == 0:
                    # transitions from white to black
                    leftEdgeNumBars += 1
                lastSeenColor = curColor
        if noteNum < totalNum-1:
            # not the last note in the connected notes
            # need to find the right edge bars
            print("not last note")
            for i in range(rightEdge.shape[0]):
                curColor = rightEdge[i]
                if lastSeenColor == 255 and curColor == 0:
                    # transitions from white to black
                    rightEdgeNumBars += 1
                lastSeenColor = curColor
        print(leftEdgeNumBars, rightEdgeNumBars)
        bars = max(leftEdgeNumBars, rightEdgeNumBars)
        if bars == 1:
            # only one bar found so eighth note
            return "eighth"
        elif bars == 2:
            # two bars found so sixteenth note
            return "sixteenth"
        else:
            raise Exception("Could not calculate duration for connected note, bars=%d"%bars)



    @staticmethod
    def getAllSubFolders(path):
        # DESCRIPTION: finds all the jpg images in the template folder
        # PARAMETERS: path: string of the path to the template folder
        # RETURN: a list of strings of the paths to all template images
        if os.path.isfile(path):
            if path[0] != "." and path.endswith(".jpg"):
                return [path]
            else:
                return []
        else:
            allPaths = []
            for filename in os.listdir(path):
                allPaths += ConnectedComponent.getAllSubFolders(path + os.sep + filename)
            return allPaths


class MeasureElem(ConnectedComponent):
    def getStaff(self, staffLines, compNum=0):
        # DESCRIPTION: finds what staff number each component is part of and alters the object .staff
        # PARAMETERS: staffLines: 2D list of all the staff lines positions
        #               compNum: the component number
        # RETURN: None
        #check more obvious cases with just y0 and y1
        if self.y1 <= staffLines[0][0]:
            self.staff = 1
            return
        elif self.y0 >= staffLines[-1][-1]:
            self.staff = len(staffLines) // 5
            return
        for staffNum in range(0, len(staffLines), 5):
            staffStart = staffLines[staffNum][0]
            staffEnd = staffLines[staffNum + 4][-1]
            if staffStart<=self.y0<=staffEnd:
                self.staff = staffNum // 5 + 1
                return
            elif staffStart<=self.y1<=staffEnd:
                self.staff = staffNum // 5 + 1
                return
            elif self.y0 < staffStart and self.y1 > staffEnd:
                self.staff = staffNum // 5 + 1
                return
        if isinstance(self,AccentComponent):
            # accent must be in the middle, just choose the closest staff
            midY = (self.y0 + self.y1)//2
            closestStaff = None
            distanceToStaff = None
            for staffNum in range(4, len(staffLines)-1, 5):
                staffMiddleStart = staffLines[staffNum][-1]
                staffMiddleEnd = staffLines[staffNum + 1][0]
                distanceToStart = abs(midY-staffMiddleStart)
                distanceToEnd = abs(midY-staffMiddleEnd)
                if distanceToStaff == None or distanceToStart < distanceToStaff:
                    closestStaff = (staffNum-4)//5 + 1
                    distanceToStaff = distanceToStart
                if distanceToEnd < distanceToStaff:
                    closestStaff = (staffNum+1)//5 +1
                    distanceToStaff = distanceToEnd
            self.staff = closestStaff
            return

        elif isinstance(self, NoteComponent) and type(self.circles) ==  np.ndarray:
            for staffNum in range(4, len(staffLines)-1, 5):
                # must be in between two staffs (like middle C)
                staffMiddleStart = staffLines[staffNum][-1]
                staffMiddleEnd = staffLines[staffNum+1][0]
                for circle in self.circles[0, :]:
                    if circle[1] >= staffMiddleStart and circle[1] <= staffMiddleEnd:
                        if self.stem == "up":
                            self.staff = (staffNum-4) // 5 + 1
                        elif self.stem == "down":
                            self.staff = (staffNum+1) // 5 + 1
                        return

        #print("Got down here")
        #print("staffLines:", staffLines)
        #print(self.y0, self.y1)
        if isinstance(self, NoteComponent) or isinstance(self, AccentComponent):
            # just find which staff middle is closest
            selfMiddle = (self.y0+self.y1)/2
            #if self.compNum == 0: print("selfMiddle", selfMiddle)
            closestStaffNum = None
            closestStaffDist = None
            for staffNum  in range(0, len(staffLines), 5):
                staffTop = staffLines[staffNum][0]
                staffBottom = staffLines[staffNum+4][-1]
                staffMiddle = (staffTop+staffBottom)/2
                #if self.compNum == 0: print("staffTop", staffTop, "staffBottom", staffBottom)
                #if self.compNum == 0: print("staffMiddle", staffMiddle)
                dist = abs(staffMiddle-selfMiddle)
                #if self.compNum == 0: print("dist", dist)
                if closestStaffDist == None or dist<closestStaffDist:
                    closestStaffDist = dist
                    closestStaffNum = (staffNum) // 5 + 1
            #if self.compNum == 0: print("closestStaff", closestStaffNum)
            #self.drawComponentOnCanvas()
            #cv2.waitKey(0)
            self.staff = closestStaffNum


        else:
            # nothing more to do
            self.staff = None
        return


class NoteComponent(MeasureElem):
    def __init__(self, x0, y0, x1, y1, label, componentImg, binaryImg, duration, stem, numPitches, staffLines, lineDist, compNum, beam=None):
        super().__init__(x0, y0, x1, y1, label, componentImg, binaryImg, compNum)
        #self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = "note"
        # durationName could be: whole, half, quarter, eighth, sixteenth
        if not (duration in ["whole", "half", "quarter", "eighth", "sixteenth"]):
            raise Exception("Duration not whole, half, quarter, eighth, sixteenth, duration=%s, compNum=%f"%(duration, self.compNum))
        assert(duration in ["whole", "half", "quarter", "eighth", "sixteenth"])
        self.durationName = duration
        self.numPitches = numPitches
        self.stem = stem
        self.staff = None
        self.circles = None
        self.pitches = []
        self.dottedPitches = []
        self.alterPitches = []
        # beam should be start, continue or end, or None if it is not part of a connected note
        # example: <beam number="1">end</beam>
        self.beam = beam
        self.findNoteheads(lineDist)
        self.getStaff(staffLines=staffLines, compNum=self.compNum)
        self.getPitches(staffLines=staffLines, distBetweenLines=lineDist)


    def findNoteheads(self, distBetweenLines):
        # DESCRIPTION: finds all the noteheads in the pitch component, alters self.circles
        # PARAMETERS: distBetweenLines: the median distance between any 2 staff lines
        # RETURN: None

        #param1 – The higher threshold of the two passed to the Canny() edge detector(the lower one is twice smaller).
        #param2 – The accumulator threshold for the circle centers at the detection stage.
        # The smaller it is, the more false circles may be detected.
        # Circles, corresponding to the larger accumulator values, will be returned first.
        idealRadius = distBetweenLines/2
        #TODO: Might be able to optimize these parameters more if they are coming out wrong
        par1 = 10
        par2 = 10
        prevDir = None
        rowOffset = 0
        if self.durationName == "eighth" or self.durationName == "sixteenth":
            # need to get rid of stem which may trigger a circle to be found
            imageHalfPoint = int(self.componentImg.shape[0]//2)
            if self.stem == "up":
                # need to get rid of top half of image
                houghComponentImg = self.componentImg[imageHalfPoint:,:]
                rowOffset = imageHalfPoint
            else:
                # need to get rid of bottom half of image
                houghComponentImg = self.componentImg[:imageHalfPoint,:]
        else:
            houghComponentImg = self.componentImg
        #Citations: [9,10,11]
        circles = cv2.HoughCircles(image=houghComponentImg, method=cv2.HOUGH_GRADIENT, dp=2.0, minDist=idealRadius+.05*idealRadius,
                                   param1=par1, param2=par2, minRadius=round(idealRadius-.05*idealRadius), maxRadius=round(idealRadius+.05*idealRadius))
        if (type(circles) !=  np.ndarray):
            circles = np.empty([1,0])
        while(circles.shape[1] != self.numPitches and par1>=2 and par2>=2 and par1<=24 and par2<=24):
            #try again with new parameters
            if circles.shape[1] < self.numPitches:
                # not enough circles, need to make more leinent
                par1 -= 1
                par2 -= 1
                dir = -1
            else:
                # too many circles found, need to make more strict
                par1 += 1
                par2 += 1
                dir = 1
            if prevDir != None and dir!=prevDir:
                # don't want to oscillate (want to find 1 circle and jumping between 0 and 2
                # find all 4 options
                circles1 = cv2.HoughCircles(image=houghComponentImg, method=cv2.HOUGH_GRADIENT, dp=2.0,
                                           minDist=idealRadius + .05 * idealRadius,
                                           param1=par1, param2=par2, minRadius=round(idealRadius - .05 * idealRadius),
                                           maxRadius=round(idealRadius + .05 * idealRadius))
                circles2 = cv2.HoughCircles(image=houghComponentImg, method=cv2.HOUGH_GRADIENT, dp=2.0,
                                            minDist=idealRadius + .05 * idealRadius,
                                            param1=par1-dir, param2=par2-dir, minRadius=round(idealRadius - .05 * idealRadius),
                                            maxRadius=round(idealRadius + .05 * idealRadius))
                circles3 = cv2.HoughCircles(image=houghComponentImg, method=cv2.HOUGH_GRADIENT, dp=2.0,
                                            minDist=idealRadius + .05 * idealRadius,
                                            param1=par1, param2=par2 - dir,
                                            minRadius=round(idealRadius - .05 * idealRadius),
                                            maxRadius=round(idealRadius + .05 * idealRadius))
                circles4 = cv2.HoughCircles(image=houghComponentImg, method=cv2.HOUGH_GRADIENT, dp=2.0,
                                            minDist=idealRadius + .05 * idealRadius,
                                            param1=par1 - dir, param2=par2,
                                            minRadius=round(idealRadius - .05 * idealRadius),
                                            maxRadius=round(idealRadius + .05 * idealRadius))
                if (type(circles1) != np.ndarray):
                    circles1 = np.empty([1, 0])
                if (type(circles2) != np.ndarray):
                    circles2 = np.empty([1, 0])
                if (type(circles3) != np.ndarray):
                    circles3 = np.empty([1, 0])
                if (type(circles4) != np.ndarray):
                    circles4 = np.empty([1, 0])
                #find the closest to the correct number, if tie, choose the lower
                circ1Dist = abs(circles1.shape[1] - self.numPitches)
                circ2Dist = abs(circles2.shape[1] - self.numPitches)
                circ3Dist = abs(circles3.shape[1] - self.numPitches)
                circ4Dist = abs(circles4.shape[1] - self.numPitches)
                minDist = min(circ1Dist, circ2Dist, circ3Dist, circ4Dist)
                circles = None
                if circ1Dist == minDist and (type(circles) != np.ndarray or circ1Dist<circles.shape[1]):
                    circles = circles1
                if circ2Dist == minDist and (type(circles) != np.ndarray or circ2Dist<circles.shape[1]):
                    circles = circles2
                if circ3Dist == minDist and (type(circles) != np.ndarray or circ3Dist<circles.shape[1]):
                    circles = circles3
                if circ4Dist == minDist and (type(circles) != np.ndarray or circ4Dist<circles.shape[1]):
                    circles = circles4
                break


            prevDir = dir
            circles = cv2.HoughCircles(image=houghComponentImg, method=cv2.HOUGH_GRADIENT, dp=2.0,
                                       minDist=idealRadius + .05 * idealRadius,
                                       param1=par1, param2=par2, minRadius=round(idealRadius - .05 * idealRadius),
                                       maxRadius=round(idealRadius + .05 * idealRadius))
            if (type(circles) != np.ndarray):
                circles = np.empty([1, 0])

        # found the correct (or at least closest) circles possible
        if (type(circles) ==  np.ndarray):
            circles = np.uint16(np.around(circles))
            for circle in circles[0, :]:
                circle[1] += rowOffset
            self.circles = circles
            #img = cv2.cvtColor(self.componentImg, cv2.COLOR_GRAY2RGB)
            #for i in circles[0, :]:
            #    cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), -1)
            #    cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), -1)

    def getPitches(self, staffLines, distBetweenLines):
        # DESCRIPTION: gets the pitch for each found notehead in self.circles, alters self.pitches
        # PARAMETERS: staffLines: 2D list representing the locations of all staff lines
        #               distBetweenLines: the median distance between any two staff lines
        # RETURN: None
        if self.staff == None or type(self.circles) !=  np.ndarray:
            return
        distanceBetweenPitches = distBetweenLines/2
        allNotes = "CDEFGAB"
        staffLocations = []
        for pitch in range(9):
            #Get all the stafflines out for the given staff you are in
            if pitch % 2 == 0:
                # it is on a staff line
                currentLine = staffLines[(self.staff - 1) * 5 + int(pitch // 2)]
                if len(currentLine) % 2 == 1:
                    staffLocations.append(currentLine[math.floor(len(currentLine) / 2)])
                else:
                    staffLocations.append(sum(currentLine) / len(currentLine))
            else:
                # it is between stafflines
                prevStaffLine = staffLocations[-1]
                nextStaffLine = staffLines[(self.staff - 1) * 5 + int((pitch + 1) // 2)]
                if len(nextStaffLine) % 2 == 1:
                    nextStaffLine = nextStaffLine[math.floor(len(nextStaffLine) / 2)]
                else:
                    nextStaffLine = sum(nextStaffLine) / len(nextStaffLine)
                staffLocations.append((nextStaffLine - prevStaffLine) / 2 + prevStaffLine)

        for circle in self.circles[0, :]:
            circleY = circle[1]+self.y0
            staffStart = staffLocations[0]
            staffEnd = staffLocations[-1]
            if circleY>=staffStart and circleY<=staffEnd:
                # we can get more accurate pitches if this is the case
                closestPitchNum = None
                closestPitchDist = None
                for pitch in range(9):
                    if closestPitchDist == None or abs(circleY-staffLocations[pitch]) < closestPitchDist:
                        closestPitchNum = pitch
                        closestPitchDist = abs(circleY-staffLocations[pitch])
                if self.staff%2 ==1:
                    # treble cleff
                    offsetPitch = 3
                    offsetOctave = 5
                else:
                    offsetPitch = 5
                    offsetOctave = 3
                getToPitch = 0
                pitch = offsetPitch
                octave = offsetOctave
                while getToPitch < closestPitchNum:
                    getToPitch += 1
                    pitch -= 1
                    if pitch < 0:
                        pitch = len(allNotes)-1
                        octave -= 1
                self.pitches.append({"step":allNotes[pitch], "octave":octave})
            elif circleY < staffStart:
                #The circle is above the five stafflines
                if self.staff%2 ==1:
                    # treble cleff
                    offsetPitch = 3
                    offsetOctave = 5
                else:
                    offsetPitch = 5
                    offsetOctave = 3
                #If the distance is less than half the circle radius away
                currentPosition = staffStart
                pitch = offsetPitch
                octave = offsetOctave
                while (abs(circleY - currentPosition) > distanceBetweenPitches/2):
                    currentPosition -= distanceBetweenPitches
                    pitch += 1
                    if pitch == len(allNotes):
                        pitch = 0
                        octave += 1
                self.pitches.append({"step": allNotes[pitch], "octave": octave})
            else:
                #The circle is below the five stafflines
                if self.staff%2 ==1:
                    # treble cleff
                    offsetPitch = 2
                    offsetOctave = 4
                else:
                    offsetPitch = 4
                    offsetOctave = 2
                currentPosition = staffEnd
                pitch = offsetPitch
                octave = offsetOctave
                while (abs(circleY - currentPosition) > distanceBetweenPitches / 2):
                    currentPosition +=  distanceBetweenPitches
                    pitch -= 1
                    if pitch < 0:
                        pitch = len(allNotes)-1
                        octave -= 1
                self.pitches.append({"step": allNotes[pitch], "octave": octave})

    def getXMLDict(self, divisions):
        # DESCRIPTION: gets the dictionary to actually give to the XML generator
        # PARAMETERS: divisions: int for the number of divisions in a quarter note
        # RETURN: dictionary with all the needed xml values and keys
        #print("Divisions when making XMLDict", divisions)
        notes = []
        for noteElemIndex in range(len(self.pitches)):
            noteDict = dict()

            #Get pitch right
            if self.alterPitches[noteElemIndex] == "sharp":
                self.pitches[noteElemIndex]["alter"] = 1
            elif self.alterPitches[noteElemIndex] == "flat":
                self.pitches[noteElemIndex]["alter"] = -1
            # should go in order: step, alter (if there is one), octave
            for key in self.pitches[noteElemIndex]:
                self.pitches[noteElemIndex][key] = str(self.pitches[noteElemIndex][key])
            #noteDict["pitch"] = self.pitches[noteElemIndex]
            noteDict["pitch"] = dict()
            noteDict["pitch"]["step"] = self.pitches[noteElemIndex]["step"]
            if "alter" in self.pitches[noteElemIndex]:
                noteDict["pitch"]["alter"] = self.pitches[noteElemIndex]["alter"]
            noteDict["pitch"]["octave"] = self.pitches[noteElemIndex]["octave"]

            #Get duration right
            if type(divisions) != int:
                divisions = round(divisions)
            if self.durationName == "quarter":
                noteDict["duration"] = str(divisions)
            elif self.durationName == "half":
                noteDict["duration"] = str(2 * divisions)
            elif self.durationName == "whole":
                noteDict["duration"] = str(4 * divisions)
            elif self.durationName == "eighth":
                noteDict["duration"] = str(int(divisions // 2))
            elif self.durationName == "sixteenth":
                noteDict["duration"] = str(int(divisions // 4))
            else:
                raise Exception("Duration not whole, half, quarter, eighth, or sixteenth")
            noteDict["type"] = str(self.durationName)
            if self.durationName != "whole":
                noteDict["stem"] = str(self.stem)
            prelimStaff = self.staff % 2
            if prelimStaff == 1:
                noteDict["staff"] = "1"
            else:
                noteDict["staff"] = "2"
            if self.dottedPitches[noteElemIndex]:
                noteDict["dot"] = None
                noteDict["duration"] = str(int(int(noteDict["duration"]) * 1.5))
            if noteElemIndex > 0:
                noteDict["chord"] = None
            if self.beam != None:
                noteDict["beam"] = self.beam
            notes.append(noteDict)
        return notes


class RestComponent(MeasureElem):
    def __init__(self, x0, y0, x1, y1, label, componentImg, binaryImg, duration, staffLines, compNum):
        super().__init__(x0, y0, x1, y1, label, componentImg, binaryImg, compNum)
        #self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = "rest"
        # durationName could be: whole, half, quarter, eighth, sixteenth
        self.durationName = duration
        self.getStaff(staffLines=staffLines, compNum=self.compNum)

    def getXMLDict(self, divisions):
        # DESCRIPTION: gets the dictionary to actually give to the XML generator
        # PARAMETERS: divisions: int for the number of divisions in a quarter note
        # RETURN: dictionary with all the needed xml values and keys

        restDict = dict()
        restDict["rest"] = None
        if self.durationName == "quarter":
            restDict["duration"] = str(divisions)
        elif self.durationName == "half":
            restDict["duration"] = str(2 * divisions)
        elif self.durationName == "whole":
            restDict["duration"] = str(4 * divisions)
        elif self.durationName == "eighth":
            restDict["duration"] = str(int(divisions // 2))
        elif self.durationName == "sixteenth":
            restDict["duration"] = str(int(divisions // 4))
        else:
            raise Exception("CompareNote type not whole, half, quarter, eighth, sixteenth")
        restDict["type"] = str(self.durationName)
        restDict["staff"] = str(self.staff % 2)
        return [restDict]

class MeasureBarComponent(MeasureElem):
    def __init__(self, x0, y0, x1, y1, label, componentImg, binaryImg, staffLines, compNum):
        super().__init__(x0, y0, x1, y1, label, componentImg, binaryImg, compNum)
        #self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = "measure bar"
        self.getStaff(staffLines=staffLines, compNum=self.compNum)

class AccentComponent(MeasureElem):
    def __init__(self, x0, y0, x1, y1, label, componentImg, binaryImg, subType, staffLines, compNum):
        super().__init__(x0, y0, x1, y1, label, componentImg, binaryImg, compNum)
        #self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = None
        self.subTypeName = subType
        self.getStaff(staffLines=staffLines, compNum=self.compNum)

class OtherComponent(ConnectedComponent):
    def __init__(self, x0, y0, x1, y1, label, componentImg, binaryImg, type, subType, compNum):
        super().__init__(x0, y0, x1, y1, label, componentImg, binaryImg, compNum)
        #self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = type
        self.subTypeName = subType

    def getTimeSignature(self):
        # DESCRIPTION: gets the time signature from the piece
        # PARAMETERS: nothing
        # RETURN: a tuple of how many beats per measure, and the beat time ((4,4), (3,4), ...)

        assert(self.typeName == "time signature")
        return self.subTypeName[0], self.subTypeName[1]

class UnknownComponent(ConnectedComponent):
    def __init__(self, x0, y0, x1, y1, label, componentImg, binaryImg, compNum, templatePath, canvasPath):
        super().__init__(x0, y0, x1, y1, label, componentImg, binaryImg, compNum)
        self.templatePath = templatePath
        self.canvasPath = canvasPath