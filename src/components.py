#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack GUI components module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from PyQt5.QtCore import Qt, QFileInfo, QSize, QObject, QThread, pyqtSignal
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from enum import Enum

import generator

#typedefs
class ButtonType(Enum):
    IMAGE = 1
    TRACK = 2
    NEW_TRACK = 3
    ARROW_UP = 4
    ARROW_DOWN = 5

CSS_SHEET_DDB = """
DragDropButton {
    background-color: rgb(255, 255, 255);
    border: 5px solid white;
}
"""

CSS_SHEET_DDB_HOVER = """
DragDropButton {
    background-color: rgb(255, 255, 255);
    border: 5px solid rgb(51, 178, 45);
}
"""

CSS_SHEET_DDB_QCF = """
QContainerFrame {
    border-top: 2px solid gray;
    border-left: 2px solid gray;
    border-bottom: 2px solid lightgray;
    border-right: 2px solid lightgray;
    
    background-color: rgb(225, 225, 225);
}

QContainerFrame:hover {
    background-color: rgb(240, 240, 240);
}
"""

CSS_SHEET_DISCENTRY = """
DiscListEntry {
    border-top: 2px solid lightgray;
    border-left: 2px solid lightgray;
    border-bottom: 2px solid gray;
    border-right: 2px solid gray;
    background-color: rgb(255, 255, 255);

    padding-top: 1px;
    padding-left: 1px;
    padding-right: 1px;
    padding-bottom: 1px;
}
"""

CSS_SHEET_NEWENTRY = """
NewDiscEntry {
    border-top: 1px solid gray;
    border-left: 2px solid gray;
    border-bottom: 2px solid lightgray;
    border-right: 2px solid lightgray;
    background-color: rgb(255, 255, 255);

    padding-top: 1px;
    padding-left: 1px;
    padding-right: 1px;
    padding-bottom: 1px;
}
"""



#dummy child of QFrame for CSS inheritance purposes
class QContainerFrame(QtWidgets.QFrame):
    pass

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

    pressed = pyqtSignal(int)
    
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

        index = self._parent.getIndex()
        self.pressed.emit(index)

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

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setAcceptDrops(True)

        #icon object
        self._img = QtWidgets.QLabel()
        self._img.setScaledContents(True)
        self.setImage(self._file)

        #child QFrame, for CSS styling purposes
        childFrame = QContainerFrame()
        childLayout = QtWidgets.QVBoxLayout()
        childLayout.setSpacing(0)
        childLayout.setContentsMargins(5, 5, 5, 5)
        childLayout.addWidget(self._img)
        childFrame.setLayout(childLayout)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(childFrame)

        self.setLayout(layout)

        #PyQt does not implement outline according to CSS standards, so
        #   two nested QWidgets are necessary to allow double border
        self.setStyleSheet(CSS_SHEET_DDB)
        childFrame.setStyleSheet(CSS_SHEET_DDB_QCF)

    def sizeHint(self):
        return(QSize(75, 75))
    
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

    def dragEnterEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        for u in event.mimeData().urls():
            u = u.toLocalFile()
            u = QFileInfo(u).completeSuffix()

            if(self._type == ButtonType.IMAGE and not u == 'png'):
                event.ignore()
                return

            if(self._type == ButtonType.TRACK and not (u == 'mp3' or u == 'wav' or u == 'ogg') ):
                event.ignore()
                return

            if(self._type == ButtonType.NEW_TRACK and not (u == 'png' or u == 'mp3' or u == 'wav' or u == 'ogg') ):
                event.ignore()
                return

        event.accept()

        #emit to signal here, highlight buttons below

        self.setStyleSheet(CSS_SHEET_DDB_HOVER)

    def dragLeaveEvent(self, event):
        event.accept()

        self.setStyleSheet(CSS_SHEET_DDB)

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        event.accept()

        f = event.mimeData().urls()
        for i, u in enumerate(f):
            f[i] = u.toLocalFile()

        if(self._type == ButtonType.NEW_TRACK):
            self.fileChanged.emit(f)

        else:
            self.setFile(f[0])
            
            #emit to signal, populate buttons below with excess files

        self.setStyleSheet(CSS_SHEET_DDB)

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
class DiscListEntry(QContainerFrame):
    def __init__(self, parent = None):
        super(DiscListEntry, self).__init__()

        self._parent = parent

        layout = QtWidgets.QHBoxLayout()

        #child widgets
        self._btnIcon = DragDropButton(ButtonType.IMAGE, self)
        self._btnTrack = DragDropButton(ButtonType.TRACK, self)
        self._leTitle = QtWidgets.QLineEdit("Track Title", self)
        self._lblIName = QtWidgets.QLabel("internal name", self)
        self._btnUpArrow = ArrowButton(ButtonType.ARROW_UP, self)
        self._btnDownArrow = ArrowButton(ButtonType.ARROW_DOWN, self)

        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        #sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

        #container layout for icon button
        iconLayout = QtWidgets.QVBoxLayout()
        iconLayout.addWidget(self._btnIcon, 0, Qt.AlignLeft)
        iconLayout.setContentsMargins(5, 5, 0, 5)
        layout.addLayout(iconLayout)

        #container layout for track button
        trackLayout = QtWidgets.QVBoxLayout()
        trackLayout.addWidget(self._btnTrack, 0, Qt.AlignLeft)
        trackLayout.setContentsMargins(5, 5, 0, 5)
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
        arrowLayout.addWidget(self._btnUpArrow, 0, Qt.AlignRight)
        arrowLayout.addWidget(self._btnDownArrow, 0, Qt.AlignRight)
        arrowLayout.setSpacing(0)
        arrowLayout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(arrowLayout)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._btnTrack.fileChanged.connect(self.setTitle)

        self.setStyleSheet(CSS_SHEET_DISCENTRY)

    def sizeHint(self):
        return QSize(350, 87.5)

    def listReorderEvent(self, count):
        index = self.getIndex()
        
        if(index <= 0):
            self._btnUpArrow.setDisabled(True)
        else:
            self._btnUpArrow.setDisabled(False)

        if(index >= count-3):
            self._btnDownArrow.setDisabled(True)
        else:
            self._btnDownArrow.setDisabled(False)

    def getIndex(self):
        return self._parent._childLayout.indexOf(self)

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
class NewDiscEntry(QContainerFrame):
    def __init__(self, parent = None):
        super(NewDiscEntry, self).__init__()

        self._parent = parent
        
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

        self._btnAdd = DragDropButton(ButtonType.NEW_TRACK, self)
        self._btnUpArrow = ArrowButton(ButtonType.ARROW_UP, self)
        self._btnDownArrow = ArrowButton(ButtonType.ARROW_DOWN, self)

        self._btnUpArrow.setDisabled(True)
        self._btnDownArrow.setDisabled(True)
        
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._btnAdd, 1)

        arrowLayout = QtWidgets.QVBoxLayout()
        arrowLayout.addWidget(self._btnUpArrow, 0, Qt.AlignRight)
        arrowLayout.addWidget(self._btnDownArrow, 0, Qt.AlignRight)
        arrowLayout.setSpacing(0)
        arrowLayout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(arrowLayout)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.setStyleSheet(CSS_SHEET_NEWENTRY)

    def sizeHint(self):
        return QSize(350, 87.5)

    def heightForWidth(self, width):
        return width * 0.375



#list of tracks
class DiscList(QtWidgets.QWidget):
    
    reordered = pyqtSignal(int)
    
    def __init__(self, parent = None):
        super(DiscList, self).__init__()

        self._parent = parent

        #create new track entry for adding new list entries
        newDiscEntry = NewDiscEntry(self)
        newDiscEntry._btnAdd.fileChanged.connect(self.addDiscEntries)

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

    def discMoveUpEvent(self, index):
        if(index == 0):
            pass
        
        #move entry up
        tmpEntry = self._childLayout.itemAt(index).widget()
        self._childLayout.removeWidget(tmpEntry)
        self._childLayout.insertWidget(index-1, tmpEntry, 0, Qt.AlignTop)

        #trigger reorder event
        self.reordered.emit(self._childLayout.count())

    def discMoveDownEvent(self, index):
        if(index == self._childLayout.count()-2):
            pass

        #move entry down
        tmpEntry = self._childLayout.itemAt(index).widget()
        self._childLayout.removeWidget(tmpEntry)
        self._childLayout.insertWidget(index+1, tmpEntry, 0, Qt.AlignTop)

        #trigger reorder event
        self.reordered.emit(self._childLayout.count())

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
        #add new entry
        tmpEntry = DiscListEntry(self)
        tmpEntry.setEntry(fIcon, fTrack, title)

        #insert into list
        self._childLayout.insertWidget(self._childLayout.count()-2, tmpEntry, 0, Qt.AlignTop)

        #bind button events
        tmpEntry._btnUpArrow.pressed.connect(self.discMoveUpEvent)
        tmpEntry._btnDownArrow.pressed.connect(self.discMoveDownEvent)

        #trigger reorder event
        self.reordered.connect(tmpEntry.listReorderEvent)
        self.reordered.emit(self._childLayout.count())

    #add multiple track objects to the list of tracks
    def addDiscEntries(self, fTrackList):
        for f in fTrackList:
            if '.png' in f:
                self.addDiscEntry(f, '', "New Track")
            else:
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
        self._btnGen = GenerateButton()
        self._btnGen.generate.connect(self.generatePacks)
        layout.addWidget(self._btnGen, 0, Qt.AlignBottom)
        
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

        #launch worker thread to generate packs
        #   FFmpeg conversion is slow, don't want to lock up UI
        self._thread = QThread()
        self._worker = GeneratePackWorker(texture_files, track_files, titles, internal_names)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.generate)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._thread.deleteLater)
        self._worker.finished.connect(self._worker.deleteLater)

        self._thread.start()

        self._btnGen.setEnabled(False)
        self._thread.finished.connect(
            lambda: self._btnGen.setEnabled(True)
        )



#worker object that generates the datapack/resourcepack in a separate QThread
class GeneratePackWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, texture_files, track_files, titles, internal_names):
        super(GeneratePackWorker, self).__init__()
        
        self._texture_files = texture_files
        self._track_files = track_files
        self._titles = titles
        self._internal_names = internal_names
    
    def generate(self):
        status = 0
        status = generator.validate(self._texture_files,
                                    self._track_files,
                                    self._titles,
                                    self._internal_names)
        if status > 0:
            self.finished.emit()
            return

        status = generator.convert_to_ogg(self._track_files,
                                          self._internal_names)
        if status > 0:
            self.finished.emit()
            return

        status = generator.generate_datapack(self._texture_files,
                                             self._track_files,
                                             self._titles,
                                             self._internal_names)
        if status > 0:
            self.finished.emit()
            return

        status = generator.generate_resourcepack(self._texture_files,
                                                 self._track_files,
                                                 self._titles,
                                                 self._internal_names)
        if status > 0:
            self.finished.emit()
            return

        print("Successfully generated datapack and resourcepack!")
        
        self.finished.emit()


