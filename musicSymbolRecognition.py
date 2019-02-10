#Will find and remove staffs
#Will characterize notes

from staffLineDetectionRemoval import staffLineDetectionRemoval

def musicSymbolRecognition(binaryImg):
    # DESCRIPTION: finds and removes all the staff lines in the original image
    # PARAMETERS: binaryImg: numpy array of the binarized image (255 or 0 in all places)
    # RETURN: staffLineRows: a 1D numpy array containing the number of black pixels in each row
    print("in musicSymbolRecognition")
    return staffLineDetectionRemoval(binaryImg)