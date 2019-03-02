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
        self.notes = []
        self.componentImg = np.copy(fullImg[y0:y1, x0:x1])
        self.circles = None

    def drawComponent(self):
        cv2.imshow("componentImg", self.componentImg)
        cv2.waitKey(0)

    def drawComponentOnCanvas(self, binaryImg):
        img = cv2.cvtColor(binaryImg, cv2.COLOR_GRAY2RGB)
        img = cv2.rectangle(img, (self.x0 - 5, self.y0 - 5), (self.x1 + 5, self.y1 + 5), (0, 0, 255), 3)
        cv2.imshow('componentOnCanvas', img)
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
        circles = cv2.HoughCircles(image=self.componentImg, method=cv2.HOUGH_GRADIENT, dp=2.0, minDist=1,
                                   param1=20, param2=13, minRadius=round(idealRadius+.05*idealRadius), maxRadius=round(idealRadius-.05*idealRadius))
        if (type(circles) ==  np.ndarray):
            circles = np.uint16(np.around(circles))
            self.circles = circles
            img = cv2.cvtColor(self.componentImg, cv2.COLOR_GRAY2RGB)
            for i in circles[0, :]:
                cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
                cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
            cv2.imshow('circles', img)


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
    singleYLines = []
    for line in staffLines:
        if len(line)%2 == 1:
            singleYLines.append(math.floor(len(line)/2))
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