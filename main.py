#File to run entire program. Main file for program that has full pianoMan function

import os
import sys
import math
import time
#import paramiko #Citations [1,2,3,4]
from pdf2image import convert_from_path #Citations [6]
from preprocessing import preprocess
from musicSymbolRecognition import musicSymbolRecognition
from staffLineDetectionRemoval import staffLineDetectionRemoval
from organizeComps import organizeComponents
from generateMusicXml import formXML
from sendToPi import sendFileToPi
import warnings #Citations [5]
warnings.filterwarnings(action='ignore',module='.*paramiko.*')
#Note for original developer:python alias to use => pythoncv


def pianoMan(shouldSend, pdfPath, fileName):
    # DESCRIPTION: runs the omr on a pdf file, attempts to save xml and send to pi in some cases
    # PARAMETERS: shouldSend: boolean, if true will send the outputXML to the raspberry pi at the end, otherwise will not
    # RETURN: None

    allPageComponents, divisions, timeSig = pianoManGetAllComponents(shouldSend=shouldSend, pdfPath=pdfPath, fileName=fileName)
    #got all the components, now need to reorganize by measures
    pianoManOrganizeAndMakeXML(shouldSend, pdfPath, fileName, allPageComponents, divisions, timeSig)



def pianoManGetAllComponents(shouldSend, pdfPath, fileName):
    startTime = time.time()
    # DESCRIPTION: runs the omr on a pdf file, attempts to save xml and send to pi in some cases
    # PARAMETERS: shouldSend: boolean, if true will send the outputXML to the raspberry pi at the end, otherwise will not
    # RETURN: None

    # need to check if the file is already in the processed library
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    libraryFileName = pdfPath[1:-4] + "-" + fileName
    libraryFileName = libraryFileName.replace("/", "-")
    libraryFilePath = scriptPath + "/library/" + libraryFileName + ".xml"
    exists = os.path.isfile(libraryFilePath)  # Citation 17
    if exists:
        # it was already processed before, don't need to process again
        outputFilePath = scriptPath + "/outBoundFiles/outputXML.xml"
        print("Working on copying")
        print("libraryFilePath", libraryFilePath)
        print("outputFilePath", outputFilePath)
        os.system('cp ' + libraryFilePath + ' ' + outputFilePath)  # Citation 18
        print("Done copy")
        if shouldSend:
            sendFileToPi("outputXML.xml")
        return

    # get the path for the pdf to use omr on
    pdfFileName = pdfPath.split(os.sep)[-1]
    jpgFileName = pdfFileName.split(".")[0]
    pdfPreFileName = pdfPath[:len(pdfPath) - len(pdfFileName)]
    pages = convert_from_path(pdfPath, 500)  # Citations [6]

    # save each page as a jpg image in the same directory
    for pageNum in range(len(pages)):
        page = pages[pageNum]
        fullJPGFileName = pdfPreFileName + jpgFileName + "-" + str(pageNum) + ".jpg"
        page.save(fullJPGFileName, 'JPEG')

    # find all components on each page separately
    allPageComponents = []
    divisions, timeSig, key = None, None, None
    for pageNum in range(len(pages)):
        print("Finding components for page %d" % (pageNum))
        imagePath = pdfPreFileName + jpgFileName + "-" + str(pageNum) + ".jpg"
        binaryImg = preprocess(path=imagePath)
        newBinaryImg, staffLineRows = staffLineDetectionRemoval(binaryImg=binaryImg)
        lineDist = getMedianLineDist(staffLines=staffLineRows)
        if pageNum == 0:
            # newMeasures, timeSig, divisions, key = musicSymbolRecognition(binaryImg=binaryImg, divisions=divisions, staffLineRows=staffLineRows, lineDist=lineDist)
            # allMeasures += newMeasures
            allComponents, timeSig, divisions = musicSymbolRecognition(binaryImg=binaryImg, divisions=divisions,
                                                                       staffLineRows=staffLineRows, lineDist=lineDist)
            allPageComponents.append((binaryImg, allComponents, lineDist))
        else:
            # Don't want to override timeSig and divisions
            # newMeasures,_,divisions,_ = musicSymbolRecognition(binaryImg=binaryImg, divisions=divisions, staffLineRows=staffLineRows, lineDist=lineDist)
            # allMeasures += newMeasures
            allComponents, _, divisions = musicSymbolRecognition(binaryImg=binaryImg, divisions=divisions,
                                                                 staffLineRows=staffLineRows, lineDist=lineDist)
            allPageComponents.append((binaryImg, allComponents, lineDist))
    endTime = time.time()
    print("pianoManGetAllComponents() time: ", endTime-startTime)
    return allPageComponents, divisions, timeSig

def pianoManOrganizeAndMakeXML(shouldSend, pdfPath, fileName, allPageComponents, divisions, timeSig):
    allMeasures = []
    for pageNum in range(len(allPageComponents)):
        print("Reorganizing components for page %d" % (pageNum))
        binaryImg, pageComponents, lineDist = allPageComponents[pageNum]
        if pageNum == 0:
            newMeasures, key = organizeComponents(binaryImg=binaryImg, connectedComponents=pageComponents,
                                                  lineDist=lineDist)
            allMeasures += newMeasures
        else:
            newMeasures, _ = organizeComponents(binaryImg=binaryImg, connectedComponents=pageComponents,
                                                lineDist=lineDist)
            allMeasures += newMeasures

    # create the xml based on the measures found
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    outputFilePath = scriptPath + "/outBoundFiles/outputXML.xml"
    formXML(allMeasures, divisions=divisions, key=key, timeBeats=timeSig[0], timeBeatType=timeSig[1], fileName=fileName,
            outputFilePath=outputFilePath)

    # create the library xml file to keep the history so don't have to process twice
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    libraryFileName = pdfPath[1:-4] + "-" + fileName
    libraryFileName = libraryFileName.replace("/", "-")
    libraryFilePath = scriptPath + "/library/" + libraryFileName + ".xml"
    formXML(allMeasures, divisions=divisions, key=key, timeBeats=timeSig[0], timeBeatType=timeSig[1], fileName=fileName,
            outputFilePath=libraryFilePath)

    # if arguments state to send the file to the raspberryPi, send it
    if shouldSend:
        sendFileToPi("outputXML.xml")


def getMedianLineDist(staffLines):
    # DESCRIPTION: gets the median difference between an of the staff line rows
    # PARAMETERS: staffLines: 2D List representing all the staff line locations on the page
    # RETURN: the median distance between any two staff lines
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



def getPDFPath(songNum):
    # DESCRIPTION: gives the end of the filePath to each of the downloaded songs
    # PARAMETERS: songNum: int representing which song we want back
    # RETURN: a string representing the end of the filepath from the main directory

    if (songNum == 0):
        return '/music_images/swansOnTheLakeEasy/Swans_on_the_lake_easy.pdf'
    elif (songNum == 1):
        return '/music_images/happyBirthday/Happy_Birthday_To_You_Piano.pdf'
    elif (songNum == 2):
        return '/music_images/youveGotAFriendInMe/Youve_Got_A_Friend_In_Me.pdf'
    elif (songNum == 3):
        return '/music_images/IKONLoveScenario/IKON_Love_Scenario.pdf'
    elif (songNum == 4):
        return '/music_images/doReMi/Do_Re_Mi.pdf'
    elif (songNum == 5):
        return '/music_images/aLoveStory/A_Love_Story.pdf'


if __name__ == "__main__":
    # Determine the command line arguments
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    pdfPath = scriptPath + getPDFPath(songNum=0)
    fileName = "Swans on the Lake"
    if len(sys.argv) == 1:
        # did not specify whether to save new file or not. Will save as default
        pianoMan(True, pdfPath, fileName)
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], bool):
        pianoMan(sys.argv[1], pdfPath, fileName)
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], str) and sys.argv[1] == "True":
        pianoMan(True, pdfPath, fileName)
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], str) and sys.argv[1] == "False":
        pianoMan(False, pdfPath, fileName)
    else:
        raise Exception("Wrong number of arguments specified. Should include 0 or 1 boolean arguments")







