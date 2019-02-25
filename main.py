#TODO: need to figure out how to convert pdf to jpg. Python is annoying here

import os
from preprocessing import preprocess
from musicSymbolRecognition import musicSymbolRecognition

#TODO: be able to handle multiple images/multiple pages
print("start")
scriptPath = os.path.dirname(os.path.realpath(__file__))
#imagePath = scriptPath+'/music_images/happyBirthday/Happy_Birthday_To_You_Piano.jpg'
imagePath = scriptPath+'/music_images/swansOnTheLakeEasy/Swans_on_the_lake_easy.jpg'

binaryImg = preprocess(path=imagePath)
print("done with preprocess")
staffLineRows = musicSymbolRecognition(binaryImg = binaryImg)
print("end")