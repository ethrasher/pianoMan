#TODO: need to figure out how to convert pdf to jpg. Python is annoying here

import os
import cv2
from pdf2image import convert_from_path
from preprocessing import preprocess
from musicSymbolRecognition import musicSymbolRecognition

#python alias with opencv => pythoncv

#pdf2image info from https://stackoverflow.com/questions/46184239/python-extract-a-page-from-a-pdf-as-a-jpeg
#TODO: be able to handle multiple images/multiple pages
print("start")
scriptPath = os.path.dirname(os.path.realpath(__file__))
# pdfPath = scriptPath+'/music_images/happyBirthday/Happy_Birthday_To_You_Piano.pdf'
pdfPath = scriptPath+'/music_images/swansOnTheLakeEasy/Swans_on_the_lake_easy.pdf'
# pdfPath = scriptPath+'/music_images/youveGotAFriendInMe/Youve_Got_A_Friend_In_Me.pdf'
# pdfPath = scriptPath+'/music_images/IKONLoveScenario/IKON_Love_Scenario.pdf'
# pdfPath = scriptPath+'/music_images/doReMi/Do_Re_Mi.pdf'
# pdfPath = scriptPath+'/music_images/aLoveStory/A_Love_Story.pdf'
pdfFileName = pdfPath.split(os.sep)[-1]
jpgFileName = pdfFileName.split(".")[0]
pdfPreFileName = pdfPath[:len(pdfPath)-len(pdfFileName)]
pages = convert_from_path(pdfPath, 500)
for pageNum in range(len(pages)):
    page = pages[pageNum]
    fullJPGFileName = pdfPreFileName+jpgFileName+"-"+str(pageNum)+".jpg"
    page.save(fullJPGFileName, 'JPEG')

imagePath = fullJPGFileName = pdfPreFileName+jpgFileName+"-"+str(0)+".jpg"
binaryImg = preprocess(path=imagePath)
print("done with preprocess")
staffLineRows = musicSymbolRecognition(binaryImg = binaryImg)
print("end")