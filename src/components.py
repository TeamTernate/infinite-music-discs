from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from enum import Enum

#typedefs
class ButtonType(Enum):
    IMAGE = 1
    TRACK = 2
    NEW_TRACK = 3



#button for generating datapack/resourcepack
class GenerateButton(QtWidgets.QPushButton):

    generate = pyqtSignal()
    
    def __init__(self, parent = None):
        super(GenerateButton, self).__init__("Generate Datapack")

        self._parent = parent

        self.setMinimumSize(200, 75)

    def mousePressEvent(self, event):
        event.accept()
        self.generate.emit()



#file selection button supporting file drag/drop
class DragDropButton(QtWidgets.QPushButton):

    fileChanged = pyqtSignal(list)
    
    def __init__(self, btnType = ButtonType.IMAGE, parent = None):
        super(DragDropButton, self).__init__(parent)

        self._parent = parent

        self._file = ''
        self._fileName = ''
        self._type = btnType

        self.setMinimumSize(50, 50)

        self._img = QtWidgets.QLabel()
        self._img.setScaledContents(True)
        self.setImage(self._file)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self._img)

        self.setLayout(layout)

        self.setStyleSheet("""
            DragDropButton {
                border: 2px solid rgb(0, 134, 63);
                background-color: rgb(225, 225, 225);
            }

            DragDropButton:on {
                border: 2px solid rgb(0, 52, 25);
            }

            DragDropButton:hover {
                border: 2px solid rgb(51, 178, 45);
            }
        """)
    
    def mousePressEvent(self, event):
        event.accept()
        
        #set accepted file types based on button function
        if(self._type == ButtonType.IMAGE):
            fileTypeStr = "Image files (*.png)"
        else:
            fileTypeStr = "Music files (*.mp3; *.wav; *.ogg)"

        f = []

        #if this action creates a new track, allow multiple files
        if(self._type == ButtonType.NEW_TRACK):
            f = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open file', '.', fileTypeStr)

            if(f[0] == []):
                return
            
            self.fileChanged.emit( f[0] )

        #if this action modifies an existing track, update one file
        else:
            f = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '.', fileTypeStr)
            
            if(f[0] == ''):
                return
            
            self.setFile(f[0])

            #wrap file string in a list to match signal type
            self.fileChanged.emit([ f[0] ])

    def hasFile(self):
        return (self._file != None)

    def getFile(self):
        return self._file

    def setFile(self, file):
        self._file = file
        self._fileName = self.getFileNameFromPath(self._file)
        self.setImage(self._file)

    def getFileNameFromPath(self, file):
        return file.split('/')[-1]

    def setImage(self, file):
        if(self._type == ButtonType.IMAGE):
            if(".png" in self._file):
                self._img.setPixmap(self.getScaledImage(QtGui.QPixmap(self._file)))
            else:
                self._img.setPixmap(self.getScaledImage(QtGui.QPixmap("../data/image-empty.png")))
        
        elif(self._type == ButtonType.TRACK):
            if(".ogg" in self._file):
                self._img.setPixmap(self.getScaledImage(QtGui.QPixmap("../data/track-ogg.png")))
            elif(".mp3" in self._file):
                self._img.setPixmap(self.getScaledImage(QtGui.QPixmap("../data/track-mp3.png")))
            elif(".wav" in self._file):
                self._img.setPixmap(self.getScaledImage(QtGui.QPixmap("../data/track-wav.png")))
            else:
                self._img.setPixmap(self.getScaledImage(QtGui.QPixmap("../data/track-empty.png")))
        
        elif(self._type == ButtonType.NEW_TRACK):
            #self._img.setPixmap(self.getScaledImage(QtGui.QPixmap("../data/image-empty-2.png")))
            pass
        
        else:
            pass

    def getScaledImage(self, pixmap):
        return pixmap.scaled(self.frameGeometry().width(), self.frameGeometry().height(), Qt.KeepAspectRatio)


#entry in list of tracks
class DiscListEntry(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(DiscListEntry, self).__init__()

        layout = QtWidgets.QHBoxLayout()

        self._btnIcon = DragDropButton(ButtonType.IMAGE, self)
        self._btnTrack = DragDropButton(ButtonType.TRACK, self)
        self._leTitle = QtWidgets.QLineEdit("Track Title", self)
        
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setLineWidth(0)
        self.setMinimumSize(200, 75)
        
        layout.addWidget(self._btnIcon, 0, Qt.AlignLeft)
        layout.addWidget(self._btnTrack, 0, Qt.AlignLeft)
        layout.addWidget(self._leTitle, 1, Qt.AlignCenter)

        arrowLayout = QtWidgets.QVBoxLayout()
        arrowLayout.addWidget(QtWidgets.QPushButton("^"), 0, Qt.AlignRight)
        arrowLayout.addWidget(QtWidgets.QPushButton("v"), 0, Qt.AlignRight)
        layout.addLayout(arrowLayout)

        self.setLayout(layout)

        self.setStyleSheet("""
            DiscListEntry {
                border: 2px solid black;
                background-color: rgb(255, 255, 255);

                padding-top: 1px;
                padding-left: 1px;
                padding-right: 1px;
                padding-bottom: 1px;
            }
        """)

    def getEntry(self):
        return [self._btnIcon.getFile(), self._btnTrack.getFile(), self._leTitle.text()]

    def setEntry(self, fIcon, fTrack, title):
        self._btnIcon.setFile(fIcon)
        self._btnTrack.setFile(fTrack)
        self._leTitle.setText(title)



#blank entry in list of tracks
class NewDiscEntry(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(NewDiscEntry, self).__init__()

        self._parent = parent
        
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setLineWidth(0)
        self.setMinimumSize(200, 75)

        self._addButton = DragDropButton(ButtonType.NEW_TRACK, self)
        
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._addButton, 1)

        arrowLayout = QtWidgets.QVBoxLayout()
        arrowLayout.addWidget(QtWidgets.QPushButton("^"), 0, Qt.AlignRight)
        arrowLayout.addWidget(QtWidgets.QPushButton("v"), 0, Qt.AlignRight)
        layout.addLayout(arrowLayout)

        self.setLayout(layout)

        self.setStyleSheet("""
            NewDiscEntry {
                border: 2px solid black;
                background-color: rgb(255, 255, 255);

                padding-top: 1px;
                padding-left: 1px;
                padding-right: 1px;
                padding-bottom: 1px;
            }
        """)



#list of tracks
class DiscList(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(DiscList, self).__init__()

        self._parent = parent

        #create new track entry for adding new list entries
        newDiscEntry = NewDiscEntry(self)
        newDiscEntry._addButton.fileChanged.connect(self.addDiscEntries)

        #child layout, contains all track entries + new track entry
        self._childLayout = QtWidgets.QVBoxLayout()
        self._childLayout.setSpacing(0)
        self._childLayout.setContentsMargins(0, 0, 0, 0)
        self._childLayout.addWidget(newDiscEntry, 0, Qt.AlignTop)
        self._childLayout.addStretch()

        #child widget, contains child layout
        widget = QtWidgets.QWidget()
        widget.setLayout(self._childLayout)

        #scroll area, contains child widget and makes child widget scrollable
        scrollArea = QtWidgets.QScrollArea(self)
        scrollArea.setWidget(widget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        #layout, contains scroll area
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

        self.setLayout(layout)

    #get all stored track data
    def getDiscEntries(self):
        entries = []
        
        for i in range(self._childLayout.count()):
            e = self._childLayout.itemAt(i).widget()

            if(type(e) == DiscListEntry):
                entries.append(e.getEntry())

        return entries

    #insert a new track object into the list of tracks
    def addDiscEntry(self, fIcon, fTrack, title):
        tmpEntry = DiscListEntry(self)
        tmpEntry.setEntry(fIcon, fTrack, title)
        
        self._childLayout.insertWidget(self._childLayout.count()-2, tmpEntry, 0, Qt.AlignTop)

    #add multiple track objects to the list of tracks
    def addDiscEntries(self, fTrackList):
        for f in fTrackList:
            self.addDiscEntry('', f, "New Track")



#primary container widget
class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(CentralWidget, self).__init__()
        
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        #list of music disc tracks
        self._discList = DiscList()
        layout.addWidget(self._discList)

        #button to generate datapack/resourcepack
        btnGen = GenerateButton()
        btnGen.generate.connect(self.generatePacks)
        layout.addWidget(btnGen, 0, Qt.AlignBottom)
        
        self.setLayout(layout)

    def generatePacks(self):
        #self._settings.getUserSettings()
        discEntries = self._discList.getDiscEntries()

        print(discEntries)

        #generator.validate()
        #generator.generate_datapack()
        #generator.generate_resourcepack()



