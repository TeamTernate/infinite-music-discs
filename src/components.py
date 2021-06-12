from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from enum import Enum

#typedefs
class ButtonType(Enum):
    IMAGE = 1
    TRACK = 2
    NEW_TRACK = 3

#button for generating datapack/resourcepack
class GenerateButton(QtWidgets.QPushButton):
    def __init__(self, text, parent = None):
        super(GenerateButton, self).__init__(text)

        self._parent = parent

        self.setMinimumSize(200, 75)

#file selection button supporting file drag/drop
class DragDropButton(QtWidgets.QPushButton):
    def __init__(self, text, btnType = ButtonType.IMAGE, parent = None):
        super(DragDropButton, self).__init__(text)

        self._parent = parent

        self._file = None
        self._fileName = ""
        self._type = btnType

        self.setMinimumSize(50, 50)

        self.setStyleSheet("""
            DragDropButton {
                border: 1px solid black;
                border-radius: 5px;
                background-color: rgb(255, 255, 255);
                text-align: center;

                padding-top: 10px;
                padding-left: 10px;
                padding-right: 10px;
                padding-bottom: 10px;
            }

            DragDropButton:pressed {
                background-color:rgb(100, 255, 100);
            }

            DragDropButton:hover {
                background-color:rgb(200, 255, 200);
            }
        """)

    def mousePressEvent(self, event):
        #set accepted file types based on button function
        if(self._type == ButtonType.IMAGE):
            fileTypeStr = "Image files (*.png)"
        else:
            fileTypeStr = "Music files (*.mp3, *.wav, *.ogg)"

        #if this action creates a new track
        if(self._type == ButtonType.NEW_TRACK):
            #allow multiple files
            f = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open file', '.', fileTypeStr)
            self._parent.addDiscEntries(f[0])

        #if this action modifies an existing track
        else:
            #update one file
            f = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '.', fileTypeStr)
            self.setFile(f[0])

    def hasFile(self):
        return (self._file != None)

    def getFile(self):
        return self._file

    def setFile(self, file):
        self._file = file
        self._fileName = self.getFileNameFromPath(self._file)
        self.setText(self._fileName)

    def getFileNameFromPath(self, file):
        return file.split('/')[-1]

#entry in list of tracks
class DiscListEntry(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(DiscListEntry, self).__init__()

        layout = QtWidgets.QHBoxLayout()

        self._btnIcon = DragDropButton("Icon", ButtonType.IMAGE, self)
        self._btnTrack = DragDropButton("Track", ButtonType.TRACK, self)
        self._leTitle = QtWidgets.QLineEdit("Track Title", self)
        
        self.setFrameShape(QtWidgets.QFrame.Box)
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
                border-radius: 10px;
                background-color: rgb(255, 255, 255);

                padding-top: 1px;
                padding-left: 1px;
                padding-right: 1px;
                padding-bottom: 1px;
            }
        """)

    def getEntry(self):
        return (self._btnIcon.getFile(), self._btnTrack.getFile(), self._leTitle.text())

    def setEntry(self, fIcon, fTrack, title):
        self._btnIcon.setFile(fIcon)
        self._btnTrack.setFile(fTrack)
        self._leTitle.setText(title)

#blank entry in list of tracks
class NewDiscEntry(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(NewDiscEntry, self).__init__()

        self._parent = parent
        
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setMinimumSize(200, 75)
        
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(DragDropButton("+", ButtonType.NEW_TRACK, self), 1)

        arrowLayout = QtWidgets.QVBoxLayout()
        arrowLayout.addWidget(QtWidgets.QPushButton("^"), 0, Qt.AlignRight)
        arrowLayout.addWidget(QtWidgets.QPushButton("v"), 0, Qt.AlignRight)
        layout.addLayout(arrowLayout)

        self.setLayout(layout)

        self.setStyleSheet("""
            NewDiscEntry {
                border: 2px solid black;
                border-radius: 10px;
                background-color: rgb(255, 255, 255);

                padding-top: 1px;
                padding-left: 1px;
                padding-right: 1px;
                padding-bottom: 1px;
            }
        """)

    def addDiscEntry(self, fIcon, fTrack, title):
        self._parent.addDiscEntry(fIcon, fTrack, title)

    def addDiscEntries(self, fTrackList):
        self._parent.addDiscEntries(fTrackList)

#list of tracks
class DiscList(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(DiscList, self).__init__()

        self._parent = parent

        self._childLayout = QtWidgets.QVBoxLayout()
        self._childLayout.addWidget(NewDiscEntry(self), 0, Qt.AlignTop)
        self._childLayout.addStretch()

        self._widget = QtWidgets.QListWidget(self)
        self._widget.setLayout(self._childLayout)

        self._scrollArea = QtWidgets.QScrollArea()
        self._scrollArea.setWidget(self._widget)
        self._scrollArea.setWidgetResizable(True)
        self._scrollArea.setVerticalScrollBarPolicy(2)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._scrollArea)

        self.setLayout(layout)

    def addDiscEntry(self, fIcon, fTrack, title):
        tmpEntry = DiscListEntry(self)
        tmpEntry.setEntry(fIcon, fTrack, title)
        
        self._childLayout.insertWidget(self._childLayout.count()-2, tmpEntry, 0, Qt.AlignTop)

    def addDiscEntries(self, fTrackList):
        for f in fTrackList:
            self.addDiscEntry('', f, "New Track")

#primary container widget
class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(CentralWidget, self).__init__()
        
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(DiscList())
        layout.addWidget(GenerateButton("Generate Datapack"), 0, Qt.AlignBottom)
        
        self.setLayout(layout)
