#need to figure out how to convert pdf to jpg. Python is annoying here

import numpy as np
import cv2
import os
import matplotlib.pyplot as plt

def binarizeImage(path):
    #DESCRIPTION: turns a jpg into a binarized version of the image as a numpy 2D array
    #PARAMETERS: path: string of the full path to the image (jpg)
    #RETURN: numpy array of the binarized image (255 or 0 in all pixels)

    #Load an color image in grayscale of the page of music
    img = cv2.imread(path, 0)
    ret,binaryImg = cv2.threshold(img,230,255,cv2.THRESH_BINARY)
    return binaryImg


def findNumBlackPixels(binaryImg):
    #DESCRIPTION: organizes the image by finding the number of black pixels per row
    #PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places)
    #RETURN: rowNums: a 1D numpy array containing the row numbers for each row
    #        amountRowBlack: a 1D numpy array containing the number of black pixels in each row
    rowNumbs = np.zeros(binaryImg.shape[0])
    amountRowBlack = np.zeros(binaryImg.shape[0])
    for i in range(binaryImg.shape[0]):
        for j in range(binaryImg.shape[1]):
            if binaryImg[i, j] == 255:
                amountRowBlack[i] += 1
        amountRowBlack[i] = binaryImg.shape[1] - amountRowBlack[i]
        rowNumbs[i] = i
    return rowNumbs, amountRowBlack

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

def plotBlackInRows(rowNumbs, amountRowBlack):
    #DESCRIPTION: plots the number of black pixels in each row of the image
    #PARAMETERS: rowNumbs: a 1D numpy array containing each row number (i.e. 1-1789)
    #            amountRowBlack: a 1D numpy array containing the number of black pixel in each row
    #RETURN: void
    #plotting the staff lines
    plt.rcParams["figure.figsize"] = (8,8)
    fig, ax = plt.subplots()
    ax.bar(rowNumbs,amountRowBlack, color="grey")
    ax.set(title="Number of Black Pixels Per Row")
    ax.set(xlabel="Row Number", ylabel="Black Pixels")
    plt.show()

def showBinaryImage(binaryImg):
    #DESCRIPTION: opens a new window and displays the image
    #PARAMETERS: binaryImage: numpy array of the binarized image (255 or 0 in all pixels)
    #RETURN: void
    cv2.imshow('image',binaryImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("end")


scriptPath = os.path.dirname(os.path.realpath(__file__))
imagePath = scriptPath+'/music_images/happyBirthday/Happy_Birthday_To_You_Piano.jpg'

binaryImg = binarizeImage(path=imagePath)
rowNumbs, amountRowBlack = findNumBlackPixels(binaryImg=binaryImg)
staffLineRows = findStaffLineRows(amountRowBlack=amountRowBlack)

plotBlackInRows(rowNumbs=rowNumbs, amountRowBlack=amountRowBlack)
showBinaryImage(binaryImg=binaryImg)
