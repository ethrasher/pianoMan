#File to run entire program. Main file for program that has full pianoMan function

import os
import sys
import paramiko #Citations [1,2,3,4]
from pdf2image import convert_from_path #Citations [6]
from preprocessing import preprocess
from musicSymbolRecognition import musicSymbolRecognition
from generateMusicXml import formXML
import warnings #Citations [5]
warnings.filterwarnings(action='ignore',module='.*paramiko.*')
#Note for original developer:python alias to use => pythoncv


def pianoMan(shouldSend):
    # DESCRIPTION: runs the omr on a pdf file, attempts to save xml and send to pi in some cases
    # PARAMETERS: shouldSend: boolean, if true will send the outputXML to the raspberry pi at the end, otherwise will not
    # RETURN: None

    # get the path for the pdf to use omr on
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    pdfPath = scriptPath + getPDFPath(songNum=0)
    pdfFileName = pdfPath.split(os.sep)[-1]
    jpgFileName = pdfFileName.split(".")[0]
    pdfPreFileName = pdfPath[:len(pdfPath) - len(pdfFileName)]
    pages = convert_from_path(pdfPath, 500) #Citations [6]

    # save each page as a jpg image in the same directory
    for pageNum in range(len(pages)):
        page = pages[pageNum]
        fullJPGFileName = pdfPreFileName + jpgFileName + "-" + str(pageNum) + ".jpg"
        page.save(fullJPGFileName, 'JPEG')

    # perform omr on each page separately and combine into allMeasures
    allMeasures = []
    for pageNum in range(len(pages)):
        imagePath = pdfPreFileName + jpgFileName + "-" + str(pageNum) + ".jpg"
        binaryImg = preprocess(path=imagePath)
        allMeasures += musicSymbolRecognition(binaryImg=binaryImg)

    # create the xml based on the measures found
    formXML(allMeasures)

    # if arguments state to send the file to the raspberryPi, send it
    if shouldSend:
        try:
            ssh = createSSHClient() #Citations [1,2,3,4]
            ftp_client = ssh.open_sftp()
            scriptPath = os.path.dirname(os.path.realpath(__file__))
            outGoingDest = scriptPath + "/outBoundFiles/outputXML.xml"
            inComingDest = "/home/pi/Desktop/PianoManProject/MusicXML_MuseScore/outputXML.xml"
            ftp_client.put(outGoingDest, inComingDest)
            ftp_client.close()
        except:
            raise Exception("Could not make connection to raspberryPi. Make sure pi is on.")


def createSSHClient():
    # DESCRIPTION: makes the connection over SSH to the raspberryPi
    # PARAMETERS: Nothing
    # RETURN: client: a paramiko SSHClient object giving the SSH connection to the raspberryPi

    client = paramiko.SSHClient() #Citations [1,2,3,4]
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname="172.26.197.78", port=22, username="pi", password="pianoMan2019")
    return client

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
    if len(sys.argv) == 1:
        # did not specify whether to save new file or not. Will save as default
        pianoMan(True)
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], bool):
        pianoMan(sys.argv[1])
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], str) and sys.argv[1] == "True":
        pianoMan(True)
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], str) and sys.argv[1] == "False":
        pianoMan(False)
    else:
        raise Exception("Wrong number of arguments specified. Should include 0 or 1 boolean arguments")







