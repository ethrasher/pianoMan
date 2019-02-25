#separates all notes through connected components
#recognizes notes
#takes in a binary image with no staff lines, and the positions of the staff lines
#returns a list of notes/symbols with position and type of note/symbol

import numpy as np
import cv2
import matplotlib.pyplot as plt

#An Object to keep track of all the connected components
#Eventually will add more here like noteheads and pitch
class ConnectedComponent(object):
    def __init__(self, x0, y0, x1, y1, label):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.label = label
        self.notes = []

def segmentationAndRecognition(binaryImg, staffLines):
    print("In segmentation/recognition")
    connectedComponents, labelImg = findConnectedComponents(binaryImg=binaryImg)
    drawConnectedComponentsAnno(binaryImg, connectedComponents)
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
    for label in range(nLabels):
        x0 = stats[label, cv2.CC_STAT_LEFT]
        y0 = stats[label, cv2.CC_STAT_TOP]
        x1 = stats[label, cv2.CC_STAT_LEFT] + stats[label, cv2.CC_STAT_WIDTH]
        y1 = stats[label, cv2.CC_STAT_TOP] + stats[label, cv2.CC_STAT_HEIGHT]
        connectedComponents.append(ConnectedComponent(x0=x0, y0=y0, x1=x1, y1=y1, label=label))
    return connectedComponents, labels





####My own attempt at connected components, buggy and slow
#Could improve, but for now just

# def findConnectedComponents(binaryImg):
#     # Return a set of ConnectedComponent Objects
#     connectedComponents = []
#     for i in range(binaryImg.shape[0]):
#         for j in range(binaryImg.shape[1]):
#             if binaryImg[i, j] == 255:
#                 makeNewComponent = True
#                 for component in connectedComponents:
#                     if ((i,j) in component.pixelSet):
#                         makeNewComponent = False
#                         break
#                 if makeNewComponent:
#                     pixelSet = connectFromPoint(binaryImg=binaryImg, pixelRow=i, pixelCol=j)
#                     x0, y0, x1, y1 = findBoundingBoxCoordinates(pixelSet=pixelSet)
#                     connectedComponents.append(ConnectedComponent(x0, y0, x1, y1))
#                     return connectedComponents
#     return connectedComponents
#
#
#
# def connectFromPoint(binaryImg, pixelRow, pixelCol):
#     directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
#     currentPix = pixelRow, pixelCol
#     pixelQueue = [currentPix]
#     seenSet = set()
#     pixelSet = set()
#     while (pixelQueue != []):
#         currentPix = pixelQueue.pop(0)
#         seenSet.add(currentPix)
#         currentColor = binaryImg[currentPix[0],currentPix[1]]
#         if (currentColor == 255):
#             #current is a black pixel
#             pixelSet.add(currentPix)
#             for dir in directions:
#                 newX = currentPix[0]+dir[0]
#                 newY = currentPix[1]+dir[1]
#                 if not((newX, newY) in seenSet):
#                     pixelQueue.append((newX, newY))
#     return pixelSet
#
# def findBoundingBoxCoordinates(pixelSet):
#     x0, y0, x1, y1 = None, None, None, None
#     for pixel in pixelSet:
#         if x0 == None or pixel[0] < x0:
#             x0 = pixel[0]
#         if y0 == None or pixel[1] < y0:
#             y0 = pixel[1]
#         if x1 == None or pixel[0] > x1:
#             x1 = pixel[0]
#         if y1 == None or pixel[1] > y1:
#             y1 = pixel[1]
#     return x0, y0, x1, y1


###VISUALIZATION/DEBUGGING FUNCTIONS
###NOT VITAL TO PERFORMANCE
def drawConnectedComponentsAnno(binaryImg, connectedComponents):
    img = cv2.cvtColor(binaryImg, cv2.COLOR_GRAY2RGB)
    print(len(connectedComponents))
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