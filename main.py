#TODO: need to figure out how to convert pdf to jpg. Python is annoying here

import numpy as np
import cv2
import os
from preprocessing import preprocess
from musicSymbolRecognition import musicSymbolRecognition


print("start")
scriptPath = os.path.dirname(os.path.realpath(__file__))
imagePath = scriptPath+'/music_images/happyBirthday/Happy_Birthday_To_You_Piano.jpg'

binaryImg = preprocess(path=imagePath)
print("done with preprocess")
staffLineRows = musicSymbolRecognition(binaryImg = binaryImg)
print("end")