#need to figure out how to convert pdf to jpg. Python is annoying here

import numpy as np
import cv2
import os

scriptPath = os.path.dirname(os.path.realpath(__file__))
#Load an color image in grayscale
img = cv2.imread(scriptPath+'/music_images/happyBirthday/Happy_Birthday_To_You_Piano.jpg', 1)
cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
print("here")