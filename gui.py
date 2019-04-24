
#Citations: 14
from tkinter import filedialog
from tkinter import *
import os
from main import pianoMan
from sendToPi import sendFileToPi
from performanceScoreEvaluator.main import main
from guiModeTemplate import ModeGUI

####################################
# GUI strucutre elements
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
            elif key == "space":
                self.text += " "
            else:
                print(key)

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
'''

####################################
# GUI modes objects
####################################
class ModeDispatcherGUI(ModeGUI):
    def __init__(self, width, height, timerDelay, sendToPi):
        super().__init__(width, height, timerDelay, sendToPi)
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        #self.backgroundImage = PhotoImage(file=scriptPath + "/guiImages/background3.gif")
        self.mode = "enterInformation"
        self.enterInfoMode = EnterInformationGUI(self.width, self.height, self.timerDelay, self.sendToPi)
        self.sendInfoMode = None

    def mousePressed(self, root, event):
        changeMode = None
        if self.mode == "enterInformation":
            changeMode = self.enterInfoMode.mousePressed(root, event)
            print(changeMode)
            if changeMode == "sendInformation":
                print("in here, making new object")
                speedLabel = self.enterInfoMode.speedLabel
                handLabel = self.enterInfoMode.handLabel
                fileNameLabel = self.enterInfoMode.fileNameLabel
                self.sendInfoMode = SendInformationGUI(self.width, self.height, self.timerDelay, self.sendToPi, speedLabel, handLabel, fileNameLabel)
        elif self.mode == "sendInformation":
            changeMode = self.sendInfoMode.mousePressed(root, event)
        if changeMode == "restart":
            self.__init__(self.width, self.height, self.timerDelay, self.sendToPi)
        elif changeMode != None:
            self.mode = changeMode

    def keyPressed(self, event):
        changeMode = None
        if self.mode == "enterInformation":
            changeMode = self.enterInfoMode.keyPressed(event)
        elif self.mode == "sendInformation":
            changeMode = self.sendInfoMode.keyPressed(event)
        if changeMode != None:
            self.mode = changeMode

    def timerFired(self):
        changeMode = None
        if self.mode == "enterInformation":
            changeMode = self.enterInfoMode.timerFired()
        elif self.mode == "sendInformation":
            changeMode = self.sendInfoMode.timerFired()
        if changeMode != None:
            self.mode = changeMode


    def redrawAll(self, canvas):
        if self.mode == "enterInformation":
            self.enterInfoMode.redrawAll(canvas)
        elif self.mode == "sendInformation":
            self.sendInfoMode.redrawAll(canvas)


class EnterInformationGUI(ModeGUI):
    def __init__(self, width, height, timerDelay, sendToPi):
        super().__init__(width, height, timerDelay, sendToPi)
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        self.musicPdfPath = ''
        self.backgroundImage = None
        self.speedLabels = ["normal", "normal-\nmedium", "medium", "medium-\nslow", "slow"]
        self.handLabels = ["bass\nclef", "treble\nclef", "both"]
        self.getFileButton = Button(x0=10, y0=self.height // 2 - 70, x1=160, y1=self.height // 2 - 20, color="black",
                                    text="Select File")
        self.speedButtons = RadioButtons(x0=110, y0=self.height // 2 + 110, x1=self.width // 2 + 50,
                                         y1=self.height // 2 + 160, text=self.speedLabels, label="Speed")

        self.handButtons = RadioButtons(x0=110, y0=self.height / 2 + 200, x1=self.width // 2 + 50,
                                        y1=self.height / 2 + 250, text=self.handLabels, label="Hands")
        self.fileNameTextBox = TextBox(x0=160, y0=self.height // 2 - 20, x1=self.width // 2, y1=self.height // 2 + 30,
                                       label="Song Name")
        self.fileNameLabel = self.fileNameTextBox.text
        self.submitButton = Button(x0=self.width - 160, y0=self.height // 2 - 70, x1=self.width - 10,
                                   y1=self.height // 2 - 20, color="dark goldenrod", text="Start")
        self.startError = ''

    def mousePressed(self, root, event):
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        if self.getFileButton.clickedInside(event.x, event.y):
            root.update()
            filepath = filedialog.askopenfilename(initialdir=scriptPath + "/music_images/", title="Select file",
                                                  filetypes=(
                                                  ("pdf files", "*.pdf"), ("all files", "*.*")))  # Citations: 15
            root.update()
            self.musicPdfPath = filepath
        self.speedButtons.clickedInside(event.x, event.y)
        self.handButtons.clickedInside(event.x, event.y)
        self.fileNameTextBox.clickedInside(event.x, event.y)
        if self.submitButton.clickedInside(event.x, event.y):
            startValues = self.checkStartValues()
            if type(startValues) == str:
                # there was an error
                self.startError = startValues
            else:
                songPath, songName, speedLabel, handLabel = startValues
                self.speedLabel = str(self.speedLabels.index(speedLabel) + 1)
                self.handLabel = handLabel.split("\n")[0]
                self.startError = 'Processing...'
                return "sendInformation"


    def checkStartValues(self):
        if self.musicPdfPath == '':
            return "No PDF File Selected"
        if self.fileNameTextBox.text == '':
            return "No Song Name"
        speedIndex = self.speedButtons.getSelectedIndex()
        handIndex = self.handButtons.getSelectedIndex()
        if speedIndex == None:
            return "No Speed Level"
        if handIndex == None:
            return "No Hand Style"
        return (self.musicPdfPath, self.fileNameTextBox.text, self.speedLabels[speedIndex], self.handLabels[handIndex])

    def keyPressed(self, event):
        self.fileNameTextBox.updateText(event.keysym)
        self.fileNameLabel = self.fileNameTextBox.text

    def timerFired(self):
        if self.backgroundImage == None:
            scriptPath = os.path.dirname(os.path.realpath(__file__))
            self.backgroundImage = PhotoImage(file=scriptPath + "/guiImages/background3.gif")
        if self.startError == "Processing...":
            pianoMan(False, self.musicPdfPath, self.fileNameTextBox.text)
            if self.sendToPi:
                sendFileToPi("outputXML.xml")
            self.startError = ""
            return "sendInformation"

    def redrawAll(self, canvas):
        canvas.create_image(0, 0, anchor=NW, image=self.backgroundImage)
        self.getFileButton.draw(canvas=canvas)
        canvas.create_rectangle(self.getFileButton.x1, self.getFileButton.y0, self.width // 2,
                                self.getFileButton.y1, fill="black")
        canvas.create_text(self.getFileButton.x1 + 10, (self.getFileButton.y0 + self.getFileButton.y1) // 2,
                           anchor="w", text=self.musicPdfPath.split("/")[-1], fill="white", font="Times 18")
        self.speedButtons.draw(canvas=canvas)
        self.handButtons.draw(canvas=canvas)
        self.fileNameTextBox.draw(canvas=canvas)
        self.submitButton.draw(canvas=canvas)
        canvas.create_rectangle(self.submitButton.x0, self.submitButton.y1, self.submitButton.x1,
                                self.submitButton.y1 + 50, fill="black")
        canvas.create_text(self.submitButton.x0, self.submitButton.y1 + 25, anchor="w", text=self.startError,
                               fill="white", font="Times 18")


class SendInformationGUI(ModeGUI):
    def __init__(self, width, height, timerDelay, sendToPi, speedLabel, handLabel, fileNameLabel):
        super().__init__(width, height, timerDelay, sendToPi)
        self.backgroundImage = None
        self.speedLabel = speedLabel
        self.handLabel = handLabel
        self.fileNameLabel = fileNameLabel
        self.sendToPiButton = Button(x0=self.width // 2 - 75, y0=self.height // 2 - 25, x1=self.width // 2 + 75,
                                     y1=self.height // 2 + 25, color="dark goldenrod", text="Start Playing")

    def mousePressed(self, root, event):
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        if self.sendToPiButton.clickedInside(event.x, event.y):
            bpmDict = {"5":49, "4":56, "3":62, "2":71, "1":83}
            bpm = bpmDict[self.speedLabel]
            contentsToWrite = "fileName:"+self.fileNameLabel+"\n"+"speed:" + str(self.speedLabel) + "\n" + "hand:" + str(self.handLabel) + "\n" + "bpm:" + str(bpm)
            self.writeFile(scriptPath + "/outBoundFiles/start.txt", contentsToWrite)
            if self.sendToPi:
                # make start file to send to the pi
                sendFileToPi("start.txt")
            # start the performance evaluator
            main()
            return "restart"
        else:
            return "sendInformation"

    def timerFired(self):
        if self.backgroundImage == None:
            scriptPath = os.path.dirname(os.path.realpath(__file__))
            self.backgroundImage = PhotoImage(file=scriptPath + "/guiImages/background3.gif")

    def redrawAll(self, canvas):
        canvas.create_image(0, 0, anchor=NW, image=self.backgroundImage)
        self.sendToPiButton.draw(canvas=canvas)


    def writeFile(self, path, contents):  # Citations
        with open(path, "wt") as f:
            f.write(contents)
'''
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
            main(data.sendToPi)
            init(data, data.sendToPi)

def keyPressed(event, data):
    # use event.char and event.keysym
    data.fileNameTextBox.updateText(event.keysym)

def timerFired(data):
    if data.startError == "Processing...":
        pianoMan(False, data.musicPdfPath, data.fileNameTextBox.text)
        if data.sendToPi:
            sendFileToPi("outputXML.xml")
        data.startError = ""
        data.mode = "sendInformation"

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
    elif data.mode == "sendInformation":
        data.sendToPiButton.draw(canvas=canvas)

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
'''

if __name__ == "__main__":
    # Determine the command line arguments
    screenWidth = 1000
    screenHeight = 600
    if len(sys.argv) == 1:
        # did not specify whether to save new file or not. Will save as default
        ModeDispatcherGUI(width=screenWidth, height=screenHeight, timerDelay=100, sendToPi=True).run()
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], bool):
        #run(width=screenWidth, height=screenHeight, sendToPi=sys.argv[1])
        ModeDispatcherGUI(width=screenWidth, height=screenHeight, timerDelay=100, sendToPi=sys.argv[1]).run()
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], str) and sys.argv[1] == "True":
        #run(width=screenWidth, height=screenHeight, sendToPi=True)
        ModeDispatcherGUI(width=screenWidth, height=screenHeight, timerDelay=100, sendToPi=True).run()
    elif len(sys.argv) == 2 and isinstance(sys.argv[1], str) and sys.argv[1] == "False":
        #run(width=screenWidth, height=screenHeight, sendToPi=False)
        ModeDispatcherGUI(width=screenWidth, height=screenHeight, timerDelay=100, sendToPi=False).run()
    else:
        raise Exception("Wrong number of arguments specified. Should include 0 or 1 boolean arguments")
'''