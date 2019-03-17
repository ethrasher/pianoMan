#going to find and remove all the staff lines in the image
#will return out a new binaryImg without the staffLines or the title information

import numpy as np
import cv2
import matplotlib.pyplot as plt


def staffLineDetectionRemoval(binaryImg):
    # DESCRIPTION: finds and removes all the staff lines in the original image
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places)
    # RETURN: newBinaryImg: a numpy array similar to the incoming binaryImg but without staff lines
    #           staffLineRows: a 1D numpy array containing the number of black pixels in each row
    print("in staffLineDetectionRemoval")
    amountRowBlack = findNumBlackPixels(binaryImg=binaryImg)
    staffLineRows = findStaffLineRows(amountRowBlack=amountRowBlack)
    #plotBlackInRows(amountRowBlack=amountRowBlack)
    noStaffBinaryImg = removeStaffLines(binaryImg=binaryImg, staffLineIndexes=staffLineRows)
    noTitleStaffBinaryImg = removeTitle(binaryImg=noStaffBinaryImg, staffLineIndexes=staffLineRows)
    showBinaryImage(binaryImg=noTitleStaffBinaryImg)
    return noTitleStaffBinaryImg, staffLineRows

def findNumBlackPixels(binaryImg):
    #DESCRIPTION: organizes the image by finding the number of black pixels per row
    #PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places)
    #RETURN: amountRowBlack: a 1D numpy array containing the number of black pixels in each row
    amountRowBlack = np.zeros(binaryImg.shape[0])
    # i is the row, j is the col
    for i in range(binaryImg.shape[0]):
        unique, counts = np.unique(binaryImg[i], return_counts=True)
        blackCounts = dict(zip(unique, counts)).get(0, 0)
        amountRowBlack[i] = blackCounts
    return amountRowBlack

def findStaffLineRows(amountRowBlack):
    #DESCRIPTION: finds the row numbers in the image where the staff lines are
    #PARAMETERS: amountRowBlack: a 1D numpy array containing the number of black pixels in each row
    #RETURN: a 2D list of row numbers in ascending order of where the staff lines are.
    #       consecutive black rows will be in a single 1D list since they are the same staff line
    thresholdRowsAmount = np.amax(amountRowBlack)*.8
    staffLineIndexes = []
    for row in range(amountRowBlack.shape[0]):
        if amountRowBlack[row] > thresholdRowsAmount:
            if staffLineIndexes == []:
                staffLineIndexes.append([row])
            else:
                lastRowAdded = staffLineIndexes[-1][-1]
                if row == lastRowAdded+1:
                    staffLineIndexes[-1].append(row)
                else:
                    staffLineIndexes.append([row])
    assert(len(staffLineIndexes)%5 == 0)
    print(staffLineIndexes)
    print(len(staffLineIndexes))
    return staffLineIndexes

def removeStaffLines(binaryImg, staffLineIndexes):
    for staffLine in staffLineIndexes:
        rowAbove = staffLine[0]-1
        rowBelow = staffLine[-1]+1
        for col in range(len(binaryImg[0])):
            blackAbove = (binaryImg[rowAbove, col] == 0)
            blackBelow = (binaryImg[rowBelow, col] == 0)
            if ((not blackAbove) and (not blackBelow)):
                for staffLineRow in staffLine:
                    binaryImg[staffLineRow, col] = 255
    return binaryImg

def removeTitle(binaryImg, staffLineIndexes):
    firstStaffLine = staffLineIndexes[0][0]
    threshold = .2
    whiteAbove = int(firstStaffLine - firstStaffLine*threshold)
    for row in range(whiteAbove):
        for col in range(len(binaryImg[0])):
            binaryImg[row,col] = 255
    return binaryImg

###VISUALIZATION/DEBUGGING FUNCTIONS
###NOT VITAL TO PERFORMANCE

def plotBlackInRows(amountRowBlack):
    #DESCRIPTION: plots the number of black pixels in each row of the image
    #PARAMETERS: amountRowBlack: a 1D numpy array containing the number of black pixel in each row
    #RETURN: void
    plt.plot(amountRowBlack)
    plt.xlabel("Row number")
    plt.ylabel("Black Pixels")
    plt.title("Number of Black Pixels Per Row")
    plt.show()

def showBinaryImage(binaryImg):
    #DESCRIPTION: opens a new window and displays the image
    #PARAMETERS: binaryImage: numpy array of the binarized image (255 or 0 in all pixels)
    #RETURN: void
    cv2.imshow('image',binaryImg)
    cv2.waitKey(0)
    #cv2.destroyAllWindows()
    print("end")