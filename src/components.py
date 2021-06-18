from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from enum import Enum

#typedefs
class ButtonType(Enum):
    IMAGE = 1
    TRACK = 2
    NEW_TRACK = 3
    ARROW_UP = 4
    ARROW_DOWN = 5



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



#button for reordering track list elements
class ArrowButton(QtWidgets.QPushButton):

    pressed = pyqtSignal()
    
    def __init__(self, btnType = ButtonType.ARROW_UP, parent = None):
        super(ArrowButton, self).__init__()

        self._parent = parent

        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)

        self._type = btnType
        if(self._type == ButtonType.ARROW_UP):
            self.setText("^")
        else:
            self.setText("v")

    def mousePressEvent(self, event):
        event.accept()
        self.pressed.emit()

    def sizeHint(self):
        return QSize(25, 25)



#file selection button supporting file drag/drop
class DragDropButton(QtWidgets.QPushButton):

    fileChanged = pyqtSignal(list)
    
    def __init__(self, btnType = ButtonType.IMAGE, parent = None):
        super(DragDropButton, self).__init__(parent)

        self._parent = parent

        self._file = ''
        self._type = btnType

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)

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
                background-color: rgb(240, 240, 240);
            }
        """)

    def sizeHint(self):
        return(QSize(50, 50))
    
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
        self.setImage(self._file)

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
            self.setText("+")
            #self._img.setPixmap(self.getScaledImage(QtGui.QPixmap("../data/image-empty-2.png")))
            pass
        
        else:
            pass

    def getScaledImage(self, pixmap):
        return pixmap.scaled(self._img.frameGeometry().width(), self._img.frameGeometry().height(), Qt.KeepAspectRatio)



#entry in list of tracks
class DiscListEntry(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(DiscListEntry, self).__init__()

        layout = QtWidgets.QHBoxLayout()

        #child widgets
        self._btnIcon = DragDropButton(ButtonType.IMAGE, self)
        self._btnTrack = DragDropButton(ButtonType.TRACK, self)
        self._leTitle = QtWidgets.QLineEdit("Track Title", self)
        self._lblIName = QtWidgets.QLabel("internal name", self)

        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        #container layout for icon button
        iconLayout = QtWidgets.QVBoxLayout()
        iconLayout.addWidget(self._btnIcon, 0, Qt.AlignLeft)
        iconLayout.setContentsMargins(10, 10, 5, 10)
        layout.addLayout(iconLayout)

        #container layout for track button
        trackLayout = QtWidgets.QVBoxLayout()
        trackLayout.addWidget(self._btnTrack, 0, Qt.AlignLeft)
        trackLayout.setContentsMargins(10, 10, 5, 10)
        layout.addLayout(trackLayout)

        #container layout for track title and internal name labels
        txtLayout = QtWidgets.QVBoxLayout()
        txtLayout.addWidget(self._leTitle, 1)
        txtLayout.addWidget(self._lblIName, 1)
        txtLayout.setSpacing(0)
        txtLayout.setContentsMargins(10, 10, 10, 10)
        layout.addLayout(txtLayout)

        #container layout for arrow buttons
        arrowLayout = QtWidgets.QVBoxLayout()
        arrowLayout.addWidget(ArrowButton(ButtonType.ARROW_UP), 0, Qt.AlignRight)
        arrowLayout.addWidget(ArrowButton(ButtonType.ARROW_DOWN), 0, Qt.AlignRight)
        arrowLayout.setSpacing(0)
        arrowLayout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(arrowLayout)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._btnTrack.fileChanged.connect(self.setTitle)

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

    def sizeHint(self):
        return QSize(200, 75)

    def getEntry(self):
        return [self._btnIcon.getFile(), self._btnTrack.getFile(), self._leTitle.text(), self._lblIName.text()]

    def setEntry(self, fIcon, fTrack, title):
        self._btnIcon.setFile(fIcon)
        self._btnTrack.setFile(fTrack)

        self.setTitle([ fTrack ])

    def setTitle(self, fFileList):
        filename = fFileList[0].split('/')[-1].split('.')[0]
        internal_name = ''.join([i for i in filename.lower() if i.isalpha()])
        
        self._leTitle.setText(filename)
        self._lblIName.setText(internal_name)
        pass



#blank entry in list of tracks
class NewDiscEntry(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(NewDiscEntry, self).__init__()

        self._parent = parent
        
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self._addButton = DragDropButton(ButtonType.NEW_TRACK, self)
        
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._addButton, 1)

        arrowLayout = QtWidgets.QVBoxLayout()
        arrowLayout.addWidget(ArrowButton(ButtonType.ARROW_UP), 0, Qt.AlignRight)
        arrowLayout.addWidget(ArrowButton(ButtonType.ARROW_DOWN), 0, Qt.AlignRight)
        arrowLayout.setSpacing(0)
        arrowLayout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(arrowLayout)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

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

    def sizeHint(self):
        return QSize(200, 75)



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

        texture_files =     []
        track_files =       []
        titles =            []
        internal_names =    []

        for e in discEntries:
            texture_files.append(e[0])
            track_files.append(e[1])
            titles.append(e[2])
            internal_names.append(e[3])

        print(texture_files, track_files, titles, internal_names)

        #generator.validate()
        #generator.generate_datapack()
        #generator.generate_resourcepack()



