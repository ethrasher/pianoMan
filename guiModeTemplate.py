from tkinter import *
####################################
# GUI mode template object
####################################
class ModeGUI(object):
    def __init__(self, width, height, timerDelay, sendToPi):
        self.width = width
        self.height = height
        self.timerDelay = timerDelay
        self.sendToPi = sendToPi

    def mousePressed(self, root, event):
        pass

    def keyPressed(self, event):
        pass

    def timerFired(self):
        pass

    def redrawAll(self, canvas):
        pass

    def run(self):
        def redrawAllWrapper(canvas):
            canvas.delete(ALL)
            canvas.create_rectangle(0, 0, self.width, self.height,
                                    fill='white', width=0)
            self.redrawAll(canvas)
            canvas.update()

        def mousePressedWrapper(root, event, canvas):
            self.mousePressed(root, event)
            redrawAllWrapper(canvas)

        def keyPressedWrapper(event, canvas):
            self.keyPressed(event)
            redrawAllWrapper(canvas)

        def timerFiredWrapper(canvas):
            self.timerFired()
            redrawAllWrapper(canvas)
            # pause, then call timerFired again
            canvas.after(self.timerDelay, timerFiredWrapper, canvas)
        # Set up data and call init
        root = Tk()
        root.resizable(width=False, height=False) # prevents resizing window

        # create the root and the canvas
        canvas = Canvas(root, width=self.width, height=self.height)
        canvas.configure(bd=0, highlightthickness=0)
        canvas.pack()
        # set up events
        #self.init()
        root.bind("<Button-1>", lambda event:
                                mousePressedWrapper(root, event, canvas))
        root.bind("<Key>", lambda event:
                                keyPressedWrapper(event, canvas))
        timerFiredWrapper(canvas)
        # and launch the app

        root.mainloop()  # blocks until window is closed