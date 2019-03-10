#separates all notes through connected components
#recognizes notes
#takes in a binary image with no staff lines, and the positions of the staff lines
#returns a list of notes/symbols with position and type of note/symbol

import numpy as np
import cv2
import math

#An Object to keep track of all the connected components
#Eventually will add more here like noteheads and pitch
class ConnectedComponent(object):
    def __init__(self, x0, y0, x1, y1, label, fullImg):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.label = label
        self.componentImg = np.copy(fullImg[y0:y1, x0:x1])
        self.circles = None
        self.stem = None
        self.staff = None
        self.pitches = []

    def drawComponent(self, windowName="componentImg"):
        cv2.imshow(windowName, self.componentImg)
        cv2.waitKey(0)

    def drawComponentOnCanvas(self, binaryImg, windowName='componentOnCanvas'):
        img = cv2.cvtColor(binaryImg, cv2.COLOR_GRAY2RGB)
        img = cv2.rectangle(img, (self.x0 - 5, self.y0 - 5), (self.x1 + 5, self.y1 + 5), (0, 0, 255), 3)
        cv2.imshow(windowName, img)
        cv2.waitKey(0)

    def findNoteheads(self, distBetweenLines):
        #information on Hough circle transform from :
        #https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghcircles/py_houghcircles.html
        #https://docs.opencv.org/2.4/modules/imgproc/doc/feature_detection.html#houghcircles
        #https://stackoverflow.com/questions/26254287/houghcircles-circle-detection-using-opencv-and-python

        #param1 – The higher threshold of the two passed to the Canny() edge detector(the lower one is twice smaller).
        #param2 – The accumulator threshold for the circle centers at the detection stage.
        # The smaller it is, the more false circles may be detected.
        # Circles, corresponding to the larger accumulator values, will be returned first.
        idealRadius = distBetweenLines/2
        #TODO: Might be able to optimize these parameters more if they are coming out wrong
        #circles = cv2.HoughCircles(image=self.componentImg, method=cv2.HOUGH_GRADIENT, dp=2.0, minDist=1,
        #                           param1=20, param2=13, minRadius=round(idealRadius+.05*idealRadius), maxRadius=round(idealRadius-.05*idealRadius))
        circles = cv2.HoughCircles(image=self.componentImg, method=cv2.HOUGH_GRADIENT, dp=2.0, minDist=idealRadius+.05*idealRadius,
                                   param1=10, param2=10, minRadius=round(idealRadius-.05*idealRadius), maxRadius=round(idealRadius+.05*idealRadius))
        if (type(circles) ==  np.ndarray):
            circles = np.uint16(np.around(circles))
            self.circles = circles
            img = cv2.cvtColor(self.componentImg, cv2.COLOR_GRAY2RGB)
            for i in circles[0, :]:
                cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), -1)
                cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), -1)
            cv2.imshow('circles', img)
            self.getStemDirection()

    def getStemDirection(self):
        lowestCircle = None
        if type(self.circles) ==  np.ndarray:
            for i in self.circles[0, :]:
                if lowestCircle == None or i[1] < lowestCircle:
                    lowestCircle = i[1]
        if lowestCircle < (self.componentImg.shape[0]//2):
            self.stem = "down"
        else:
            self.stem = "up"

    def getStaff(self, staffLines):
        #check more obvious cases with just y0 and y1
        for staffNum in range(0, len(staffLines), 5):
            staffStart = staffLines[staffNum][0]
            staffEnd = staffLines[staffNum + 4][-1]
            if staffStart<=self.y0<=staffEnd:
                self.staff = staffNum // 5 + 1
            elif staffStart<=self.y1<=staffEnd:
                self.staff = staffNum // 5 + 1
            elif self.y0 < staffStart and self.y1 > staffEnd:
                self.staff = staffNum // 5 + 1
            if (self.staff != None):
                return
        if self.staff == None or self.circles==None:
            # if the component doesn't have a circle there is nothing more I can do.
            # self.staff will remain None
            return

        #checking easier cases again at top and bottom
        if self.y1<=staffLines[0][0]:
            self.staff = 1
            return
        elif self.y0>=staffLines[-1][-1]:
            self.staff = staffNum // 5 + 1
            return
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
            staffEnd = staffLocations[1]
            if circleY>=staffStart and circleY<=staffEnd:
                # we can get more accurate pitches if this is the case
                closestPitchNum = None
                closestPitchDist = None
                for pitch in range(9):
                    if closestPitchDist == None or abs(circleY-staffLocations[pitch]) < closestPitchNum:
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
                    if pitch == 0:
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



def segmentationAndRecognition(binaryImg, staffLines):
    print("In segmentation/recognition")
    connectedComponents, labelImg = findConnectedComponents(binaryImg=binaryImg)
    #first connected component
    drawConnectedComponentsAnno(binaryImg, connectedComponents)
    lineDist = getAverageLineDist(staffLines=staffLines)
    print("Number of CC:", len(connectedComponents))
    for comp in connectedComponents:
        comp.drawComponentOnCanvas(binaryImg=binaryImg)
        comp.drawComponent()
        comp.findNoteheads(lineDist)
        print("Done finding noteheads")
        comp.getStaff(staffLines=staffLines)
        print("staff:", comp.staff)
        comp.getPitches(staffLines=staffLines, distBetweenLines=lineDist)
        print("pitches:", comp.pitches)
    return connectedComponents

def findConnectedComponents(binaryImg):
    # Citations:
    # see https://stackoverflow.com/questions/35854197/how-to-use-opencvs-connected-components-with-stats-in-python
    # see https://www.programcreek.com/python/example/89340/cv2.connectedComponentsWithStats

    connectivity = 8
    invertedImg = cv2.bitwise_not(binaryImg)
    nLabels, labels, stats, centroids = cv2.connectedComponentsWithStats(invertedImg, connectivity, cv2.CV_32S)
    # nLabels is the number of connected components
    # stats is a matrix of the size of nLabels (one label for each component) with 5 items, left, top, width, height, area
    connectedComponents = []
    #TODO: Remove cc's that are smaller than a certain size threshold (i.e. 1 or 2 pixels) from the image and don't make object
    for label in range(nLabels):
        x0 = stats[label, cv2.CC_STAT_LEFT]
        y0 = stats[label, cv2.CC_STAT_TOP]
        x1 = stats[label, cv2.CC_STAT_LEFT] + stats[label, cv2.CC_STAT_WIDTH]
        y1 = stats[label, cv2.CC_STAT_TOP] + stats[label, cv2.CC_STAT_HEIGHT]
        connectedComponents.append(ConnectedComponent(x0=x0, y0=y0, x1=x1, y1=y1, label=label, fullImg=binaryImg))
    return connectedComponents, labels

def getAverageLineDist(staffLines):
    print("In get averageLineDist")
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


###VISUALIZATION/DEBUGGING FUNCTIONS
###NOT VITAL TO PERFORMANCE
def drawConnectedComponentsAnno(binaryImg, connectedComponents):
    img = cv2.cvtColor(binaryImg, cv2.COLOR_GRAY2RGB)
    for cc in connectedComponents:
        img = cv2.rectangle(img, (cc.x0-5, cc.y0-5), (cc.x1+5, cc.y1+5), (0, 255, 0), 3)
    cv2.imshow('image', img)
    cv2.waitKey(0)

def drawContours(binaryImg):
    contours, hierarchy = cv2.findContours(binaryImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    backtorgb = cv2.cvtColor(binaryImg,cv2.COLOR_GRAY2RGB)
    im = cv2.drawContours(backtorgb, contours, -1, (0, 255, 0), 1)
    cv2.imshow('image', im)
    cv2.waitKey(0)