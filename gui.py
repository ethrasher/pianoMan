
#Citations: 14
from tkinter import filedialog
from tkinter import *
import os
from main import pianoManGetAllComponents, pianoManOrganizeAndMakeXML
from connectedCompObj import UnknownComponent
from sendToPi import sendFileToPi
from performanceScoreEvaluator.main import main
from PIL import ImageTk,Image
import xml.etree.ElementTree as ET


####################################
# GUI structure elements
####################################

class Button(object):
    def __init__(self, x0, y0, x1, y1, color, text):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.color = color
        self.text = text

    def clickedInside(self, x, y):
        if self.x0 <= x and x <= self.x1 and self.y0 <= y and y<= self.y1:
            return True
        return False

    def draw(self, canvas):
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, fill=self.color, width=3, outline="dark goldenrod")
        canvas.create_text((self.x0+self.x1)/2, (self.y0+self.y1)/2, text = self.text, fill = "white", font="Times 25")


class RadioButton(Button):
    def __init__(self, x0, y0, x1, y1, color, text):
        super().__init__(x0, y0, x1, y1, color, text)
        self.selected = False

    def draw(self, canvas):
        # put button on top half
        verticalDiameter = (self.y1+self.y0)/2 - self.y0
        horizontalDiameter = self.x1-self.x0
        radius = min(verticalDiameter, horizontalDiameter)/2
        ccY = (self.y1-self.y0)*1/4 + self.y0
        ccX = (self.x0+self.x1)/2
        canvas.create_oval(ccX-radius, ccY-radius, ccX+radius, ccY+radius, fill="white")
        if self.selected:
            canvas.create_oval(ccX-radius*.6, ccY-radius*.6, ccX+radius*.6, ccY+radius*.6, fill="black")
        #textY = (self.y1-self.y0)*3/4 + self.y0
        textY = (self.y1-self.y0)*1/2 + self.y0 + 10
        textX = (self.x0+self.x1)/2
        canvas.create_text(textX, textY, anchor="n", text=self.text, fill="white", font="Times 18")


class RadioButtons(object):
    def __init__(self, x0, y0, x1, y1, text, label):
        self.buttons = []
        width = (x1-x0)/len(text)
        for i in range(len(text)):
            startX = x0+width*i
            endX = x0+width*(i+1)
            self.buttons.append(RadioButton(x0=startX, y0=y0, x1=endX, y1=y1, color="white", text=text[i]))
        self.x0 = x0
        self.y0=y0
        self.x1=x1
        self.y1=y1
        self.text=text
        self.label = label

    def clickedInside(self, x, y):
        clickedIndex = None
        for i in range(len(self.buttons)):
            if self.buttons[i].clickedInside(x, y):
                clickedIndex = i
                break
        if clickedIndex != None:
            for i in range(len(self.buttons)):
                if i == clickedIndex:
                    self.buttons[i].selected = True
                else:
                    self.buttons[i].selected = False
        return clickedIndex != None

    def draw(self, canvas):
        canvas.create_rectangle(self.x0-100, self.y0-10, self.x1+10, self.y1+25, fill="black")
        canvas.create_text(self.x0 - 50, (self.y1 + self.y0) / 2, fill="white",
                           text=self.label, font="Times 25")
        for button in self.buttons:
            button.draw(canvas)

    def getSelectedIndex(self):
        for i in range(len(self.buttons)):
            if self.buttons[i].selected:
                return i
        return None


class TextBox(object):
    def __init__(self, x0, y0, x1, y1, label):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.selected = False
        self.text = ''
        self.label = label

    def clickedInside(self, x, y):
        if self.x0 <= x and x <= self.x1 and self.y0 <= y and y <= self.y1:
            self.selected = True
        else:
            self.selected = False

    def updateText(self, key):
        if self.selected:
            if len(key) == 1 and key.isalnum():
                self.text += key
            elif key == "BackSpace":
                self.text = self.text[:-1]
            elif key == "period":
                self.text += "."
            elif key == "-":
                self.text += "-"
            elif key == "underscore":
                self.text += "_"
            else:
                pass

    def draw(self, canvas):
        canvas.create_rectangle(self.x0-150, self.y0, self.x0, self.y1, fill="black")
        canvas.create_text(self.x0 - 75, (self.y1 + self.y0) / 2, fill="white",
                           text=self.label, font="Times 25")
        if self.selected:
            width = 5
        else:
            width=1
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, fill="white", outline="dark goldenrod", width = width)
        canvas.create_text(self.x0+5, (self.y0+self.y1)/2, anchor="w", text = self.text, fill="black", font="Times 18")


def checkStartValues(data):
    if data.musicPdfPath == '':
        return "No PDF File Selected"
    if data.fileNameTextBox.text == '':
        return "No Song Name"
    speedIndex = data.speedButtons.getSelectedIndex()
    handIndex = data.handButtons.getSelectedIndex()
    if speedIndex == None:
        return "No Speed Level"
    if handIndex == None:
        return "No Hand Style"
    return (data.musicPdfPath, data.fileNameTextBox.text, data.speedLabels[speedIndex], data.handLabels[handIndex])

def writeFile(path, contents): #Citations
    with open(path, "wt") as f:
        f.write(contents)

def readFile(path): #Citations
    with open(path, "rt") as f:
        return f.read()

def getMaxPageNumber(pdfPath):
    pdfFileName = pdfPath.split(os.sep)[-1]
    jpgFileName = pdfFileName.split(".")[0]
    pdfPreFileName = pdfPath[:len(pdfPath) - len(pdfFileName)]
    maxPageNum = 0
    fullJPGFileName = pdfPreFileName + jpgFileName + "-" + str(maxPageNum) + ".jpg"
    exists = os.path.isfile(fullJPGFileName)
    while exists:
        maxPageNum += 1
        fullJPGFileName = pdfPreFileName + jpgFileName + "-" + str(maxPageNum) + ".jpg"
        exists = os.path.isfile(fullJPGFileName)
    if maxPageNum == 0:
        raise Exception("No jpgs of the pages exist")
    return maxPageNum-1

def getJPGImages(data):
    pdfPath = data.musicPdfPath
    maxPageNumber = getMaxPageNumber(pdfPath)
    pdfFileName = pdfPath.split(os.sep)[-1]
    jpgFileName = pdfFileName.split(".")[0]
    pdfPreFileName = pdfPath[:len(pdfPath) - len(pdfFileName)]
    for pageNum in range(maxPageNumber+1):
        fullJPGFileName = pdfPreFileName + jpgFileName + "-" + str(pageNum) + ".jpg"
        pillowPageImage = Image.open(fullJPGFileName)
        scale = 1/11
        pillowPageImage = pillowPageImage.resize((int(pillowPageImage.size[0]*scale), int(pillowPageImage.size[1]*scale)), Image.ANTIALIAS) #Citation 20
        currentMusicPage = ImageTk.PhotoImage(pillowPageImage)
        data.musicPageImages.append(currentMusicPage)

def getAbletonInstructionImages(data):
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    instructionPath = scriptPath + "/AbletonInstructions/"
    data.abletonInstructionBegin = []
    data.abletonInstructionEnd = []
    newHeight = 450
    for i in range(7):
        fullFileName = instructionPath + "instruction" + str(i) + ".png"
        pillowImage = Image.open(fullFileName)
        # need height to be 500
        scale = newHeight / pillowImage.size[1]
        pillowImage = pillowImage.resize((int(pillowImage.size[0]*scale), newHeight), Image.ANTIALIAS)  # Citation 20
        currentInstruction = ImageTk.PhotoImage(pillowImage)
        data.abletonInstructionBegin.append(currentInstruction)
    for i in range(7,11):
        fullFileName = instructionPath + "instruction" + str(i) + ".png"
        pillowImage = Image.open(fullFileName)
        # need height to be 500
        scale = newHeight / pillowImage.size[1]
        pillowImage = pillowImage.resize((int(pillowImage.size[0]*scale), newHeight), Image.ANTIALIAS)  # Citation 20
        currentInstruction = ImageTk.PhotoImage(pillowImage)
        data.abletonInstructionEnd.append(currentInstruction)

def getUnknownComponentLocations(allPageComponents):
    locations = []
    for pageNum in range(len(allPageComponents)):
        allComponents = allPageComponents[pageNum][1]
        for compNum in range(len(allComponents)):
            curComponent = allComponents[compNum]
            if isinstance(curComponent, UnknownComponent):
                locations.append((pageNum, compNum))
    return locations

def getUnknownComponentImages(data):
    for location in data.unknownCompLocations:
        unknownComp = data.allPageComponents[location[0]][1][location[1]]
        fullJPGCompPath = unknownComp.templatePath
        pillowPageImage = Image.open(fullJPGCompPath)
        # want it to be no bigger than 150 by 150
        scaleWidth = 150 / pillowPageImage.size[0]
        scaleHeight = 150 / pillowPageImage.size[1]
        scale = min(scaleWidth, scaleHeight)
        pillowPageImage = pillowPageImage.resize(
            (int(pillowPageImage.size[0] * scale), int(pillowPageImage.size[1] * scale)),
            Image.ANTIALIAS)  # Citation 20
        currentUnknownCompImage = ImageTk.PhotoImage(pillowPageImage)
        #data.unknownCompImages.append(currentUnknownCompImage)

        #get the canvas image
        fullJPGCanvasPath = unknownComp.canvasPath
        pillowPageImage = Image.open(fullJPGCanvasPath)
        # want it to be no bigger than 150 by 150
        scaleHeight = 450 / pillowPageImage.size[1]
        scale = min(scaleWidth, scaleHeight)
        pillowPageImage = pillowPageImage.resize(
            (int(pillowPageImage.size[0] * scale), int(pillowPageImage.size[1] * scale)),
            Image.ANTIALIAS)  # Citation 20
        currentUnknownCanvasImage = ImageTk.PhotoImage(pillowPageImage)
        data.unknownImages.append((currentUnknownCompImage, currentUnknownCanvasImage))

def getXMLTimeSig():
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    path = scriptPath + "/outBoundFiles/outputXML.xml"
    tree = ET.parse(path) # From https://docs.python.org/2/library/xml.etree.elementtree.html
    root = tree.getroot()
    # 2 gets to part
    # 0 gets to first measure
    # 0 gets to attributes
    # 2 gets to time
    time = root[2][0][0][2]
    timeSigTop = time.find('beats').text
    timeSigBottom = time.find('beat-type').text
    return (timeSigTop, timeSigBottom)

def getPerformanceValues(data):
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    path = scriptPath + "/outBoundFiles/end.txt"
    allValues = readFile(path)
    data.performanceValues = []
    for line in allValues.split("\n"):
        data.performanceValues.append(line)

def init(data, sendToPi):
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    data.backgroundImage = PhotoImage(file=scriptPath + "/guiImages/background3.gif")
    data.titleImage = PhotoImage(file=scriptPath + "/guiImages/title.gif")
    data.musicPdfPath = ''
    data.getFileButton = Button(x0=10, y0=data.height//2-70, x1=160, y1=data.height//2-20, color="black", text="Select File")
    data.fileNameTextBox = TextBox(x0=160, y0=data.height//2-20, x1=data.width//2, y1=data.height//2+30, label="Song Name")
    data.speedLabels = ["normal", "normal-\nmedium", "medium", "medium-\nslow", "slow"]
    data.speedButtons = RadioButtons(x0=110, y0=data.height//2+110, x1=data.width//2 +50, y1=data.height//2+160, text = data.speedLabels, label="Speed")
    data.speedLabel = None
    data.handLabels = ["bass\nclef", "treble\nclef", "both"]
    data.handButtons = RadioButtons(x0=110, y0=data.height/2+200, x1=data.width//2 +50, y1=data.height/2+250, text=data.handLabels, label="Hands")
    data.handLabel = None
    data.submitButton = Button(x0=data.width-160, y0=data.height//2-70, x1=data.width-10, y1=data.height//2-20, color="dark goldenrod", text="Start")
    data.musicPdfPath = ''
    data.startError = ''
    data.sendToPi = sendToPi
    data.sendToPiButton = Button(x0=data.width//2-75, y0=data.height//2-25, x1=data.width//2+75, y1=data.height//2+25, color="dark goldenrod", text="Start Playing")
    # music sheet image stuff
    data.nextPageButton = Button(x0=data.width//2+10, y0=data.height-60, x1=data.width//2+110, y1 = data.height-10, color = "black", text = "Next")
    data.prevPageButton = Button(x0=data.width//2-110, y0=data.height-60, x1=data.width//2-10, y1 = data.height-10, color = "black", text = "Prev")
    data.donePageButton = Button(x0=data.width-110, y0=data.height-60, x1=data.width-10, y1 = data.height-10, color = "dark goldenrod", text = "Done")
    data.currentPageNumber = 0
    data.maxPageNumber = 0
    data.musicPageImages = []
    # ableton instruction stuff
    data.nextInstructionButton = Button(x0=data.width // 2 + 10, y0=data.height - 60, x1=data.width // 2 + 110,
                                 y1=data.height - 10, color="black", text="Next")
    data.prevInstructionButton = Button(x0=data.width // 2 - 110, y0=data.height - 60, x1=data.width // 2 - 10,
                                 y1=data.height - 10, color="black", text="Prev")
    data.skipInstructionButton = Button(x0=data.width - 110, y0=data.height - 60, x1=data.width - 10, y1=data.height - 10,
                                 color="dark goldenrod", text="Skip")
    data.currentInstructionNumber = 0
    getAbletonInstructionImages(data)
    # explaining performance stuff
    data.donePerformanceButton = Button(x0=data.width//2 - 25, y0=data.height - 60, x1=data.width//2 + 50, y1=data.height - 10,
                                 color="dark goldenrod", text="Done")
    data.explainPerformanceDimensions = (200, data.height//3 + 10, data.width-200, data.height-70)
    #from pianoMan
    data.allPageComponents = None
    data.divisions = None
    data.timeSig = None
    data.unknownCompLocations = None
    data.unknownImages = []
    data.currentUnknownCompNumber = 0
    #mode switcher
    data.mode = "enterInformation"


def mousePressed(root, event, data):
    # use event.x and event.y
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    if data.mode == "enterInformation":
        if data.getFileButton.clickedInside(event.x, event.y):
            root.update()
            filepath = filedialog.askopenfilename(initialdir=scriptPath + "/music_images/", title="Select file",
                                                       filetypes=(("pdf files", "*.pdf"), ("all files", "*.*"))) #Citations: 15
            root.update()
            data.musicPdfPath = filepath
        data.speedButtons.clickedInside(event.x, event.y)
        data.handButtons.clickedInside(event.x, event.y)
        data.fileNameTextBox.clickedInside(event.x, event.y)
        if data.submitButton.clickedInside(event.x, event.y):
            startValues = checkStartValues(data)
            if type(startValues) == str:
                #there was an error
                data.startError = startValues
            else:
                songPath, songName, speedLabel, handLabel = startValues
                data.speedLabel = str(data.speedLabels.index(speedLabel) + 1)
                data.handLabel = handLabel.split("\n")[0]
                data.startError = 'Processing...'
    elif data.mode == "abletonInstructionBegin":
        if data.skipInstructionButton.clickedInside(event.x, event.y):
            data.mode = "sendInformation"
            data.currentInstructionNumber = 0
        elif data.nextInstructionButton.clickedInside(event.x, event.y):
            if data.currentInstructionNumber == len(data.abletonInstructionBegin)-1:
                data.mode = "sendInformation"
                data.currentInstructionNumber = 0
            data.currentInstructionNumber = min(len(data.abletonInstructionBegin)-1, data.currentInstructionNumber+1)
        elif data.prevInstructionButton.clickedInside(event.x, event.y):
            data.currentInstructionNumber = max(0, data.currentInstructionNumber - 1)
    elif data.mode == "sendInformation":
        if data.sendToPiButton.clickedInside(event.x, event.y):
            bpmDict = {"5":49, "4":56, "3":62, "2":71, "1":83}
            bpm = bpmDict[data.speedLabel]
            contentsToWrite = "fileName:"+data.fileNameTextBox.text+"\n"+"speed:" + str(data.speedLabel) + "\n" + "hand:" + str(data.handLabel) + "\n" + "bpm:" + str(bpm)
            writeFile(scriptPath + "/outBoundFiles/start.txt", contentsToWrite)
            if data.sendToPi:
                # make start file to send to the pi
                sendFileToPi("start.txt")
            # start the performance evaluator
            getJPGImages(data)
            data.mode = "showMusicImages"
    elif data.mode == "showMusicImages":
        if data.donePageButton.clickedInside(event.x, event.y):
            data.mode = "abletonInstructionEnd"
        elif data.nextPageButton.clickedInside(event.x, event.y):
            data.currentPageNumber = min(data.maxPageNumber, data.currentPageNumber+1)
        elif data.prevPageButton.clickedInside(event.x, event.y):
            data.currentPageNumber = max(0, data.currentPageNumber - 1)
    elif data.mode == "abletonInstructionEnd":
        if data.skipInstructionButton.clickedInside(event.x, event.y):
            data.mode = "checkPerformanceScore"
        elif data.nextInstructionButton.clickedInside(event.x, event.y):
            if data.currentInstructionNumber == len(data.abletonInstructionEnd)-1:
                data.mode = "checkPerformanceScore"
            data.currentInstructionNumber = min(len(data.abletonInstructionEnd)-1, data.currentInstructionNumber+1)
        elif data.prevInstructionButton.clickedInside(event.x, event.y):
            data.currentInstructionNumber = max(0, data.currentInstructionNumber - 1)
    elif data.mode == "explainPerformanceScore":
        if data.donePerformanceButton.clickedInside(event.x, event.y):
            performance_path = ''
            end_path = ''
            try:
                scriptPath = os.path.dirname(os.path.realpath(__file__))
                performance_path = scriptPath + "/performanceScoreEvaluator/midi/performance.mid"
                os.remove(performance_path)
                end_path = scriptPath + "/outBoundFiles/end.txt"
                os.remove(end_path)
            except OSError:
                print("performance path: ", performance_path)
                print("end path: ", end_path)
                print("Error while deleting files.")
            init(data, data.sendToPi)


def keyPressed(event, data):
    # use event.char and event.keysym
    data.fileNameTextBox.updateText(event.keysym)

def timerFired(data):
    if data.startError == "Processing...":
        #pianoMan(False, data.musicPdfPath, data.fileNameTextBox.text)
        pianoOutComps = pianoManGetAllComponents(shouldSend=False, pdfPath=data.musicPdfPath, fileName=data.fileNameTextBox.text)
        if pianoOutComps != None:
            data.allPageComponents, data.divisions, data.timeSig = pianoOutComps
            data.unknownCompLocations = getUnknownComponentLocations(data.allPageComponents)
            pianoManOrganizeAndMakeXML(shouldSend=False, pdfPath=data.musicPdfPath, fileName=data.fileNameTextBox.text, allPageComponents=data.allPageComponents, divisions=data.divisions, timeSig = data.timeSig)
        else:
            # still need to know time sig for gui
            # need to parse outputXML for it
            data.timeSig = getXMLTimeSig()
        if data.sendToPi:
            sendFileToPi("outputXML.xml")
        pdfPath = data.musicPdfPath
        data.maxPageNumber = getMaxPageNumber(pdfPath)
        data.startError = ""
        data.mode = "abletonInstructionBegin"
    elif data.mode == "checkPerformanceScore":
        main(data.sendToPi)
        getPerformanceValues(data)
        data.mode = "explainPerformanceScore"

def redrawAll(canvas, data):
    # draw in canvas
    canvas.create_image(0, 0, anchor=NW, image=data.backgroundImage)
    if data.mode == "enterInformation":
        data.getFileButton.draw(canvas=canvas)
        canvas.create_rectangle(data.getFileButton.x1, data.getFileButton.y0, data.width//2, data.getFileButton.y1, fill="black")
        canvas.create_text(data.getFileButton.x1+10, (data.getFileButton.y0+data.getFileButton.y1)//2, anchor="w", text=data.musicPdfPath.split("/")[-1], fill="white", font="Times 18")
        data.speedButtons.draw(canvas=canvas)
        data.handButtons.draw(canvas=canvas)
        data.fileNameTextBox.draw(canvas=canvas)
        data.submitButton.draw(canvas=canvas)
        canvas.create_rectangle(data.submitButton.x0, data.submitButton.y1, data.submitButton.x1, data.submitButton.y1+50, fill="black")
        canvas.create_text(data.submitButton.x0, data.submitButton.y1+25, anchor="w", text=data.startError, fill="white", font="Times 18")
    elif data.mode == "abletonInstructionBegin":
        currentInstruction = data.abletonInstructionBegin[data.currentInstructionNumber]
        canvas.create_image(data.width//2, data.height//2, image=currentInstruction)
        if data.currentInstructionNumber == 4:
            # on the bpm page
            canvas.create_rectangle(data.width//2 - 200, data.height//2+100, data.width//2 + 200, data.height//2 + 200, fill="black", width=3, outline="white")
            canvas.create_text(data.width//2, data.height//2 + 120, text = "BPM to use:", fill="white", font = "Times 30 bold")
            if data.speedLabel == "1":
                speed = "83.00"
            elif data.speedLabel == "2":
                speed = "71.00"
            elif data.speedLabel == "3":
                speed = "62.00"
            elif data.speedLabel == "4":
                speed = "56.00"
            elif data.speedLabel == "5":
                speed = "49.00"
            else:
                raise Exception("not possible speed label: %s"%str(data.speedLabel))
            canvas.create_text(data.width//2, data.height//2 + 160, text = speed, fill="white", font="Times 25 bold")
        elif data.currentInstructionNumber == 5:
            # on the time sig page
            canvas.create_rectangle(data.width//2 - 200, data.height//2+100, data.width//2 + 200, data.height//2 + 200, fill="black", width=3, outline="white")
            canvas.create_text(data.width//2, data.height//2 + 120, text = "Time Signature to use:", fill="white", font = "Times 30 bold")
            canvas.create_text(data.width//2, data.height//2 + 160, text = data.timeSig[0]+"/"+data.timeSig[1], fill="white", font="Times 25 bold")

        data.nextInstructionButton.draw(canvas=canvas)
        data.prevInstructionButton.draw(canvas=canvas)
        data.skipInstructionButton.draw(canvas=canvas)
        labelX0 = data.width//2 - 150
        labelX1 = data.width//2 + 150
        canvas.create_rectangle(labelX0, 0, labelX1, 60, fill = "black")
        canvas.create_text(data.width//2, 30, text = "Instructions", font = "Times 40", fill = "white")
    elif data.mode == "sendInformation":
        data.sendToPiButton.draw(canvas=canvas)
    elif data.mode == "showMusicImages":
        # show the sheet music image for the correct page
        currentMusicPage = data.musicPageImages[data.currentPageNumber]
        canvas.create_image(data.width//2, 0, anchor=N, image=currentMusicPage)
        data.nextPageButton.draw(canvas=canvas)
        data.prevPageButton.draw(canvas=canvas)
        data.donePageButton.draw(canvas=canvas)
    elif data.mode == "abletonInstructionEnd":
        currentInstruction = data.abletonInstructionEnd[data.currentInstructionNumber]
        canvas.create_image(data.width//2, data.height//2, image=currentInstruction)

        data.nextInstructionButton.draw(canvas=canvas)
        data.prevInstructionButton.draw(canvas=canvas)
        data.skipInstructionButton.draw(canvas=canvas)
        labelX0 = data.width // 2 - 150
        labelX1 = data.width // 2 + 150
        canvas.create_rectangle(labelX0, 0, labelX1, 60, fill="black")
        canvas.create_text(data.width // 2, 30, text="Instructions", font="Times 40", fill="white")
    elif data.mode == "checkPerformanceScore":
        canvas.create_rectangle(data.width//2-150, data.height//2-35, data.width//2+150, data.height//2+35, fill="dark goldenrod", width=0)
        canvas.create_text(data.width//2, data.height//2, text="Evaluating Performance...", fill="white", font="Times 25")
    elif data.mode == "explainPerformanceScore":
        data.donePerformanceButton.draw(canvas=canvas)
        canvas.create_rectangle(data.explainPerformanceDimensions[0], data.explainPerformanceDimensions[1],
                            data.explainPerformanceDimensions[2], data.explainPerformanceDimensions[3], fill="black")
        items = ["Hits: correctly played", "Miss: missed the note entirely", "Wrong: wrong note is played",
                 "Span: played the correct note for the wrong duration", "Early: played the note too early",
                 "Late: played the note too late"]
        numOfScores = len(items)+1.5
        itemHeight = (data.explainPerformanceDimensions[3]-data.explainPerformanceDimensions[1])//numOfScores
        titleHeight = itemHeight*1.5
        # draw the title
        canvas.create_text(data.width//2, data.explainPerformanceDimensions[1]+10, anchor="n", text="Performance Measure Explainations", font="Times 30", fill="white")
        # draw each item
        for i in range(len(items)):
            itemTitle = items[i].split(": ")[0]
            itemDescription = items[i].split(": ")[1]
            canvas.create_text(data.width//2 - 100, data.explainPerformanceDimensions[1]+10+titleHeight+itemHeight*i, anchor="nw", text=itemTitle, font="Times 18", fill="white")
            canvas.create_text(data.width // 2 - 10,
                           data.explainPerformanceDimensions[1] + 10 + titleHeight + itemHeight * i, anchor="nw",
                           text=itemDescription, font="Times 18", fill="white")

        # draw the actual score values
        canvas.create_rectangle(0, data.explainPerformanceDimensions[1], data.explainPerformanceDimensions[0], data.explainPerformanceDimensions[3], fill="dark goldenrod")
        height = (data.explainPerformanceDimensions[3] - data.explainPerformanceDimensions[1])//(1+len(data.performanceValues))
        canvas.create_text(data.explainPerformanceDimensions[0]//2, data.explainPerformanceDimensions[1] + height//2, text = "Scores", font = "Times 18 bold", fill="black")
        for i in range(len(data.performanceValues)):
            canvas.create_text(data.explainPerformanceDimensions[0]//2, data.explainPerformanceDimensions[1]+height*(i+1), text=data.performanceValues[i], font="Times 18", fill="black")


    elif data.mode == "findUnknownComponents":
        currentCompImage = data.unknownImages[data.currentUnknownCompNumber][0]
        currentCanvasImage = data.unknownImages[data.currentUnknownCompNumber][1]
        canvas.create_image(0, 0 , anchor="nw", image = currentCanvasImage)
        canvas.create_image(75, data.height-75, image=currentCompImage)



####################################
# use the run function as-is
####################################

def run(width=300, height=300, sendToPi=True):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(root, event, canvas, data):
        mousePressed(root, event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    root.title("PianoMan")
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    init(data, sendToPi)
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(root, event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app

    root.mainloop()  # blocks until window is closed

#run(1000, 600)




if __name__ == "__main__":
    # Determine the command line arguments
    screenWidth = 1000
    screenHeight = 600
    if len(sys.argv) == 1:
        # did not specify whether to save new file or not. Will save as default
        run(width=screenWidth, height=screenHeight, sendToPi=True)
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], bool):
        run(width=screenWidth, height=screenHeight, sendToPi=sys.argv[1])
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], str) and sys.argv[1] == "True":
        run(width=screenWidth, height=screenHeight, sendToPi=True)
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], str) and sys.argv[1] == "False":
        run(width=screenWidth, height=screenHeight, sendToPi=False)
    else:
        raise Exception("Wrong number of arguments specified. Should include 0 or 1 boolean arguments")
