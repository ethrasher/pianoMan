import os
import paramiko
from pdf2image import convert_from_path
from preprocessing import preprocess
from musicSymbolRecognition import musicSymbolRecognition
from generateMusicXml import formXML

#From: https://github.com/ansible/ansible/issues/52598
import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

#Information about paramiko from:
#http://docs.paramiko.org/en/2.4/api/client.html
#https://medium.com/@keagileageek/paramiko-how-to-ssh-and-file-transfers-with-python-75766179de73
#https://github.com/paramiko/paramiko
#https://stackoverflow.com/questions/250283/how-to-scp-in-python

#python alias with opencv => pythoncv
def createSSHClient():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname="172.26.197.78", port=22, username="pi", password="pianoMan2019")
    return client

#pdf2image info from https://stackoverflow.com/questions/46184239/python-extract-a-page-from-a-pdf-as-a-jpeg
print("start")
scriptPath = os.path.dirname(os.path.realpath(__file__))
pdfPath = scriptPath+'/music_images/swansOnTheLakeEasy/Swans_on_the_lake_easy.pdf'
# pdfPath = scriptPath+'/music_images/happyBirthday/Happy_Birthday_To_You_Piano.pdf'
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

allMeasures = []
for pageNum in range(len(pages)):
    imagePath = fullJPGFileName = pdfPreFileName+jpgFileName+"-"+str(pageNum)+".jpg"
    binaryImg = preprocess(path=imagePath)
    print("done with preprocess")
    allMeasures += musicSymbolRecognition(binaryImg = binaryImg)
formXML(allMeasures)
print("made XML file")
# scp Piano_Man_Piano.jpg pi@172.26.197.78:Desktop/PianoManProject/MusicXML_MuseScore/PianoMan.jpg
ssh = createSSHClient()
ftp_client=ssh.open_sftp()
scriptPath = os.path.dirname(os.path.realpath(__file__))
outGoingDest = scriptPath + "/outBoundFiles/outputXML.xml"
inComingDest = "/home/pi/Desktop/PianoManProject/MusicXML_MuseScore/outputXML.xml"
ftp_client.put(outGoingDest,inComingDest)
ftp_client.close()
print("end")