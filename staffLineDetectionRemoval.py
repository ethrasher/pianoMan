import numpy as np
import cv2
import os
import matplotlib.pyplot as plt


def staffLineDetectionRemoval(binaryImg):
    # DESCRIPTION: finds and removes all the staff lines in the original image
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places)
    # RETURN: staffLineRows: a 1D numpy array containing the number of black pixels in each row
    print("in staffLineDetectionRemoval")
    amountRowBlack = findNumBlackPixels(binaryImg=binaryImg)
    staffLineRows = findStaffLineRows(amountRowBlack=amountRowBlack)
    plotBlackInRows(amountRowBlack=amountRowBlack)
    return staffLineRows

def findNumBlackPixels(binaryImg):
    #DESCRIPTION: organizes the image by finding the number of black pixels per row
    #PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places)
    #RETURN: amountRowBlack: a 1D numpy array containing the number of black pixels in each row
    rowNumbs = np.zeros(binaryImg.shape[0])
    amountRowBlack = np.zeros(binaryImg.shape[0])
    print("starting long loop")
    for i in range(binaryImg.shape[0]):
        for j in range(binaryImg.shape[1]):
            if binaryImg[i, j] == 255:
                amountRowBlack[i] += 1
        amountRowBlack[i] = binaryImg.shape[1] - amountRowBlack[i]
        rowNumbs[i] = i
    print("end of long loop")
    return amountRowBlack

def findStaffLineRows(amountRowBlack):
    #DESCRIPTION: finds the row numbers in the image where the staff lines are
    #PARAMETERS: amountRowBlack: a 1D numpy array containing the number of black pixels in each row
    #RETURN: a list of row numbers in ascending order of where the staff lines are
    thresholdRowsAmount = np.amax(amountRowBlack)*.8
    staffLineIndexes = []
    for row in range(amountRowBlack.shape[0]):
        if amountRowBlack[row] > thresholdRowsAmount and (staffLineIndexes == [] or row-1 != staffLineIndexes[-1]):
            staffLineIndexes.append(row)
    print(staffLineIndexes)
    print(len(staffLineIndexes))
    return staffLineIndexes


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
