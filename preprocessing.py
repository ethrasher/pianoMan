#File to handle the preprocessing of the music sheet
#Fairly limited because we are assuming we are getting an ideal scan

import cv2

def preprocess(path):
    # DESCRIPTION: turns a jpg into a binarized version of the image as a numpy 2D array
    # May handle other issues as well as less ideal scans come up
    # PARAMETERS: path: string of the full path to the image (jpg)
    # RETURN: numpy array of the binarized image (255 or 0 in all pixels)
    binaryImg = binarizeImage(path)
    showBinaryImage(binaryImg=binaryImg)
    return binaryImg

def binarizeImage(path):
    #DESCRIPTION: turns a jpg into a binarized version of the image as a numpy 2D array
    #PARAMETERS: path: string of the full path to the image (jpg)
    #RETURN: numpy array of the binarized image (255 or 0 in all pixels)
    img = cv2.imread(path, 0) #Load an color image in grayscale of the page of music
    ret,binaryImg = cv2.threshold(img,230,255,cv2.THRESH_BINARY)
    return binaryImg


###VISUALIZATION/DEBUGGING FUNCTIONS
###NOT VITAL TO PERFORMANCE
def showBinaryImage(binaryImg):
    #DESCRIPTION: opens a new window and displays the image
    #PARAMETERS: binaryImage: numpy array of the binarized image (255 or 0 in all pixels)
    #RETURN: void
    cv2.imshow('image',binaryImg)
    cv2.waitKey(0)
    #cv2.destroyAllWindows()
    print("end")