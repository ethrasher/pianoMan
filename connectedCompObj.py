#An Object to keep track of all the connected components
#Eventually will add more here like noteheads and pitch
import cv2
import math
import os
import numpy as np

class ConnectedComponent(object):
    def __init__(self, x0, y0, x1, y1, label, componentImg):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.label = label
        self.componentImg = componentImg

    def drawComponent(self, windowName="componentImg"):
        cv2.imshow(windowName, self.componentImg)

    def saveComponent(self, compNum):
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        compPath = scriptPath + '/templates/component%d.jpg'%(compNum)
        cv2.imwrite(compPath, self.componentImg)

    def drawComponentOnCanvas(self, binaryImg, windowName='componentOnCanvas'):
        img = cv2.cvtColor(binaryImg, cv2.COLOR_GRAY2RGB)
        img = cv2.rectangle(img, (self.x0 - 5, self.y0 - 5), (self.x1 + 5, self.y1 + 5), (0, 0, 255), 6)
        cv2.imshow(windowName, img)

    def templateMatch(self, staffLines, lineDist, compNum=0):
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
            self.saveComponent(compNum=compNum)
            return
        templatePath = bestTemplatePath.split("templates/")[1]
        return self.makeTemplateObject(bestTemplatePath, staffLines, lineDist, compNum)

    def makeTemplateObject(self, templatePath, staffLines, lineDist, compNum):
        if templatePath.find("aaa_note_whole") >= 0:
            # it is a whole note
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="whole", stem=None, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=compNum)
        elif templatePath.find("aaa_note_half") >= 0:
            # it is a half note
            stemDirString = templatePath.split("/")[-2]
            if stemDirString == "stemUp": stem = "up"
            elif stemDirString == "stemDown": stem = "down"
            else: raise Exception("Could not get stem for half note, compNum:" + str(compNum))
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="half", stem=stem, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=compNum)
        elif templatePath.find("aaa_note_quarter") >= 0:
            # it is a quarter note
            stemDirString = templatePath.split("/")[-2]
            if stemDirString == "stemUp":
                stem = "up"
            elif stemDirString == "stemDown":
                stem = "down"
            else:
                raise Exception("Could not get stem for quarter note, compNum:" + str(compNum))
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="quarter", stem=stem, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=compNum)
        elif templatePath.find("aaa_note_eighth") >= 0:
            # it is an eighth note
            stemDirString = templatePath.split("/")[-2]
            if stemDirString == "stemUp":
                stem = "up"
            elif stemDirString == "stemDown":
                stem = "down"
            else:
                raise Exception("Could not get stem for half note, compNum:" + str(compNum))
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="eighth", stem=stem, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=compNum)
        elif templatePath.find("aaa_note_sixteenth") >= 0:
            stemDirString = templatePath.split("/")[-2]
            if stemDirString == "stemUp":
                stem = "up"
            elif stemDirString == "stemDown":
                stem = "down"
            else:
                raise Exception("Could not get stem for half note, compNum:" + str(compNum))
            return NoteComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="sixteenth", stem=stem, numPitches=1,
                                 staffLines=staffLines, lineDist=lineDist, compNum=compNum)
        elif templatePath.find("aaa_note_chord") >= 0:
            # it is a multi-note chord
            typeName = "note"
            subTypeName = "chord"
            durationName = (templatePath.split("/")[2]).split("_")[1]
            #TODO: DEAL WITH THIS CASE
        elif templatePath.find("aaa_note_connected") >= 0:
            # it is a series of connected notes
            typeName = "note"
            subTypeName = "connected"
            durationName = None
            #TODO: DEAL WITH THIS CASE


        elif templatePath.find("aaa_rest_whole") >= 0:
            # it is a whole rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="whole", staffLines=staffLines,
                                 compNum=compNum)
        elif templatePath.find("aaa_rest_half") >= 0:
            # it is a half rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="half", staffLines=staffLines,
                                 compNum=compNum)
        elif templatePath.find("aaa_rest_quarter") >= 0:
            # it is a quarter rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="quarter", staffLines=staffLines,
                                 compNum=compNum)
        elif templatePath.find("aaa_rest_eighth") >= 0:
            # it is an eighth rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="eighth", staffLines=staffLines,
                                 compNum=compNum)
        elif templatePath.find("aaa_rest_sixteenth") >= 0:
            # it is a sixteenth rest
            return RestComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                 componentImg=self.componentImg, duration="sixteenth", staffLines=staffLines,
                                 compNum=compNum)


        elif templatePath.find("aaa_measure_bar") >= 0:
            # it is a measure_barx0, y0, x1, y1, label, componentImg, staffLines, compNum
            return MeasureBarComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label, componentImg=self.componentImg, staffLines=staffLines, compNum=compNum)


        elif templatePath.find("aaa_accent") >= 0:
            #it is an accent
            subType = templatePath.split("/")[-2]
            return AccentComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label, componentImg=self.componentImg, subType=subType, staffLines=staffLines, compNum=compNum)


        elif templatePath.find("aaa_clef_treble") >= 0:
            # it is a treble_clef
            type = "clef"
            subType = "treble"
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, type=type, subType=subType, compNum=compNum)
        elif templatePath.find("aaa_clef_base") >= 0:
            # it is a base_clef
            type = "clef"
            subType = "base"
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, type=type, subType=subType, compNum=compNum)
        elif templatePath.find("aaa_timeSignature") >= 0:
            # it is a timeSig
            type = "time signature"
            subType = templatePath.split("/")[-2]
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, type=type, subType=subType, compNum=compNum)
        elif templatePath.find("aaa_staveSwirl") >= 0:
            # it is a stave Swirl
            type = "stave swirl"
            subType = None
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, type=type, subType=subType, compNum=compNum)
        elif templatePath.find("aaa_alphaNum") >= 0:
            # it is an alpha-numeric character
            type = "alphaNum"
            subType = None
            return OtherComponent(x0=self.x0, y0=self.y0, x1=self.x1, y1=self.y1, label=self.label,
                                  componentImg=self.componentImg, type=type, subType=subType, compNum=compNum)


    @staticmethod
    def getAllSubFolders(path):
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

        elif isinstance(self, NoteComponent) and self.circles!=None:
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
        return


class NoteComponent(MeasureElem):
    def __init__(self, x0, y0, x1, y1, label, componentImg, duration, stem, numPitches, staffLines, lineDist, compNum):
        super().__init__(x0, y0, x1, y1, label, componentImg)
        self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = "note"
        # durationName could be: whole, half, quarter, eighth, sixteenth
        self.durationName = duration
        self.numPitches = numPitches
        self.stem = stem
        self.getStaff(staffLines=staffLines, compNum=compNum)
        self.circles = None
        self.pitches = []
        self.findNoteheads(lineDist)
        self.getPitches(staffLines=staffLines, distBetweenLines=lineDist)
        self.dottedPitches = []
        self.alterPitches = []

    def findNoteheads(self, distBetweenLines):
        #param1 – The higher threshold of the two passed to the Canny() edge detector(the lower one is twice smaller).
        #param2 – The accumulator threshold for the circle centers at the detection stage.
        # The smaller it is, the more false circles may be detected.
        # Circles, corresponding to the larger accumulator values, will be returned first.
        idealRadius = distBetweenLines/2
        #TODO: Might be able to optimize these parameters more if they are coming out wrong
        #Citations: [9,10,11]
        circles = cv2.HoughCircles(image=self.componentImg, method=cv2.HOUGH_GRADIENT, dp=2.0, minDist=idealRadius+.05*idealRadius,
                                   param1=10, param2=10, minRadius=round(idealRadius-.05*idealRadius), maxRadius=round(idealRadius+.05*idealRadius))
        if (type(circles) ==  np.ndarray):
            circles = np.uint16(np.around(circles))
            self.circles = circles
            img = cv2.cvtColor(self.componentImg, cv2.COLOR_GRAY2RGB)
            for i in circles[0, :]:
                cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), -1)
                cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), -1)

    def getPitches(self, staffLines, distBetweenLines):
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
        notes = []
        for noteElemIndex in range(len(self.pitches)):
            noteDict = dict()
            if self.alterPitches[noteElemIndex] == "sharp":
                self.pitches[noteElemIndex]["alter"] = 1
            elif self.alterPitches[noteElemIndex] == "flat":
                self.pitches[noteElemIndex]["alter"] = -1
            for key in self.pitches[noteElemIndex]:
                self.pitches[noteElemIndex][key] = str(self.pitches[noteElemIndex][key])
            noteDict["pitch"] = self.pitches[noteElemIndex]
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
            noteDict["type"] = str(self.durationName)
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
            notes.append(noteDict)
        return notes


class RestComponent(MeasureElem):
    def __init__(self, x0, y0, x1, y1, label, componentImg, duration, staffLines, compNum):
        super().__init__(x0, y0, x1, y1, label, componentImg)
        self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = "rest"
        # durationName could be: whole, half, quarter, eighth, sixteenth
        self.durationName = duration
        self.getStaff(staffLines=staffLines, compNum=compNum)

    def getXMLDict(self, divisions):
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
        restDict["type"] = str(self.durationName)
        restDict["staff"] = str(self.staff % 2)
        return [restDict]

class MeasureBarComponent(MeasureElem):
    def __init__(self, x0, y0, x1, y1, label, componentImg, staffLines, compNum):
        super().__init__(x0, y0, x1, y1, label, componentImg)
        self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = "measure bar"
        self.getStaff(staffLines=staffLines, compNum=compNum)

class AccentComponent(MeasureElem):
    def __init__(self, x0, y0, x1, y1, label, componentImg, subType, staffLines, compNum):
        super().__init__(x0, y0, x1, y1, label, componentImg)
        self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = None
        self.subTypeName = subType
        self.getStaff(staffLines=staffLines, compNum=compNum)

class OtherComponent(ConnectedComponent):
    def __init__(self, x0, y0, x1, y1, label, componentImg, type, subType, compNum):
        super().__init__(x0, y0, x1, y1, label, componentImg)
        self.compNum = compNum
        # typeName could be: note, rest, measure bar, accent, clef, time signature, stave swirl, or alphaNum
        self.typeName = type
        self.subTypeName = subType

    def getTimeSignature(self):
        assert(self.typeName == "time signature")
        return (self.subTypeName[0], self.subTypeName[1])