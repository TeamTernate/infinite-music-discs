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

#typedefs and constants
class ButtonType(Enum):
    IMAGE = 1
    TRACK = 2
    NEW_TRACK = 3
    ARROW_UP = 4
    ARROW_DOWN = 5

class FileExt():
    PNG = 'png'
    MP3 = 'mp3'
    WAV = 'wav'
    OGG = 'ogg'

class Assets():
    ICON_ICON_EMPTY =   '../data/image-empty.png'
    ICON_TRACK_EMPTY =  '../data/track-empty.png'
    ICON_NEW_DISC =     '../data/new-disc.png'
    ICON_MP3 =          '../data/track-mp3.png'
    ICON_WAV =          '../data/track-wav.png'
    ICON_OGG =          '../data/track-ogg.png'

class StyleProperties():
    DRAG_HELD = "drag_held"
    ALPHA =     "alpha"

CSS_SHEET_SUBTITLE = """
QLabel {
    color: gray;
    font-style: italic;
}
"""

CSS_SHEET_DRAGDROPBUTTON = """
DragDropButton {
    background-color: rgb(255, 255, 255);
    border: 5px solid white;
}

DragDropButton[drag_held="true"] {
    border: 5px solid rgb(51, 178, 45);
}

DragDropButton[alpha="9"] {
    border: 5px solid rgba(51, 178, 45, 0.9);
}

DragDropButton[alpha="8"] {
    border: 5px solid rgba(51, 178, 45, 0.8);
}

DragDropButton[alpha="7"] {
    border: 5px solid rgba(51, 178, 45, 0.7);
}

DragDropButton[alpha="6"] {
    border: 5px solid rgba(51, 178, 45, 0.6);
}

DragDropButton[alpha="5"] {
    border: 5px solid rgba(51, 178, 45, 0.5);
}

DragDropButton[alpha="4"] {
    border: 5px solid rgba(51, 178, 45, 0.4);
}

DragDropButton[alpha="3"] {
    border: 5px solid rgba(51, 178, 45, 0.3);
}

DragDropButton[alpha="2"] {
    border: 5px solid rgba(51, 178, 45, 0.2);
}

DragDropButton[alpha="1"] {
    border: 5px solid rgba(51, 178, 45, 0.1);
}

QContainerFrame {
    border-top: 2px solid gray;
    border-left: 2px solid gray;
    border-bottom: 2px solid lightgray;
    border-right: 2px solid lightgray;
    
    background-color: rgb(225, 225, 225);
}

QContainerFrame[drag_held="true"] {
    border-top: 2px solid rgb(100, 128, 100);
    border-left: 2px solid rgb(100, 128, 100);
    border-bottom: 2px solid rgb(190, 211, 190);
    border-right: 2px solid rgb(190, 211, 190);
    
    background-color: rgb(195, 240, 195);
}

QContainerFrame:hover {
    background-color: rgb(240, 240, 240);
}
"""

CSS_SHEET_NEWDISCBUTTON = """
NewDiscButton {
    border-top: 2px solid gray;
    border-left: 2px solid gray;
    border-bottom: 2px solid lightgray;
    border-right: 2px solid lightgray;
    
    background-color: rgb(225, 225, 225);
}

NewDiscButton:hover {
    background-color: rgb(240, 240, 240);
}

NewDiscButton:hover[drag_held="true"] {
    border-top: 2px solid gray;
    border-left: 2px solid gray;
    border-bottom: 2px solid lightgray;
    border-right: 2px solid lightgray;
    
    background-color: rgb(195, 240, 195);
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
    padding-top: 1px;
    padding-left: 1px;
    padding-right: 1px;
    padding-bottom: 1px;
}
"""



#dummy child of QFrame for CSS inheritance purposes
class QContainerFrame(QtWidgets.QFrame):
    pass

#Child of QLineEdit with text autoselect on click
class QFocusLineEdit(QtWidgets.QLineEdit):
    def focusInEvent(self, event):
        self._wasFocused = False

    def mousePressEvent(self, event):
        super(QFocusLineEdit, self).mousePressEvent(event)

        if not self._wasFocused:
            self.selectAll()

        self._wasFocused = True

#button for generating datapack/resourcepack
class GenerateButton(QtWidgets.QPushButton):

    generate = pyqtSignal()
    
    def __init__(self, parent = None):
        super(GenerateButton, self).__init__("Generate Datapack")

        self._parent = parent

        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)

    def sizeHint(self):
        return QSize(350, 87.5)

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

    def sizeHint(self):
        return QSize(25, 25)

    def mousePressEvent(self, event):
        event.accept()

        index = self._parent.getIndex()
        self.pressed.emit(index)



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

    def sizeHint(self):
        return(QSize(75, 75))

    def mousePressEvent(self, event):
        event.accept()

    def dragEnterEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        for u in event.mimeData().urls():
            u = u.toLocalFile()
            u = QFileInfo(u).completeSuffix()

            if(self.supportsFiletype(u)):
                event.accept()
            else:
                event.ignore()

    def dragLeaveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def repolish(self, obj):
        obj.style().unpolish(obj)
        obj.style().polish(obj)

    def hasFile(self):
        return (self._file != None)

    def getFile(self):
        return self._file

    def setFile(self, file):
        self._file = file
        self.setImage(self._file)

    def setImage(self, file):
        f = QFileInfo(file).completeSuffix()

        assetDict = {
            FileExt.PNG: self._file,
            FileExt.OGG: Assets.ICON_OGG,
            FileExt.MP3: Assets.ICON_MP3,
            FileExt.WAV: Assets.ICON_WAV
        }

        imgPath = ''
        if(self._type == ButtonType.IMAGE):
            imgPath = assetDict.get(f, Assets.ICON_ICON_EMPTY)
        elif(self._type == ButtonType.TRACK):
            imgPath = assetDict.get(f, Assets.ICON_TRACK_EMPTY)
        elif(self._type == ButtonType.NEW_TRACK):
            self.setText('+')
            #imgPath = assetDict.get(f, Assets.ICON_NEW_DISC)
        else:
            pass

        self._img.setPixmap(self.getScaledImage(QtGui.QPixmap(imgPath)))

    def getScaledImage(self, pixmap):
        return pixmap.scaled(self._img.frameGeometry().width(), self._img.frameGeometry().height(), Qt.KeepAspectRatio)

    def supportsFiletype(self, ext):
        if(self._type == ButtonType.IMAGE):
            return ( ext in [ FileExt.PNG ] )
        if(self._type == ButtonType.TRACK):
            return ( ext in [ FileExt.MP3, FileExt.WAV, FileExt.OGG ] )
        if(self._type == ButtonType.NEW_TRACK):
            return ( ext in [ FileExt.MP3, FileExt.WAV, FileExt.OGG, FileExt.PNG ] )



class FileButton(DragDropButton):
    def __init__(self, btnType = ButtonType.IMAGE, parent = None):
        super(FileButton, self).__init__(btnType, parent)

        #child QFrame, for CSS styling purposes
        self._childFrame = QContainerFrame()
        childLayout = QtWidgets.QVBoxLayout()
        childLayout.setSpacing(0)
        childLayout.setContentsMargins(5, 5, 5, 5)
        childLayout.addWidget(self._img)
        self._childFrame.setLayout(childLayout)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self._childFrame)

        self.setLayout(layout)

        #PyQt does not implement outline according to CSS standards, so
        #   two nested QWidgets are necessary to allow double border
        self.setProperty(StyleProperties.DRAG_HELD, False)
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, False)
        self.setStyleSheet(CSS_SHEET_DRAGDROPBUTTON)

    def mousePressEvent(self, event):
        super(FileButton, self).mousePressEvent(event)

        #set accepted file types based on button function
        if(self._type == ButtonType.IMAGE):
            fileTypeStr = "Image files (*.png)"
        else:
            fileTypeStr = "Music files (*.mp3; *.wav; *.ogg)"

        f = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '.', fileTypeStr)

        if(f[0] == ''):
            return

        self.setFile(f[0])

        #wrap file string in a list to match signal type
        self.fileChanged.emit([ f[0] ])

    def dragEnterEvent(self, event):
        super(FileButton, self).dragEnterEvent(event)
        if not event.isAccepted():
            return

        #emit to signal here, highlight buttons below

        self.setProperty(StyleProperties.DRAG_HELD, True)
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, True)
        self.repolish(self)
        self.repolish(self._childFrame)

    def dragLeaveEvent(self, event):
        super(FileButton, self).dragLeaveEvent(event)

        self.setProperty(StyleProperties.DRAG_HELD, False)
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, False)
        self.repolish(self)
        self.repolish(self._childFrame)

    def dropEvent(self, event):
        super(FileButton, self).dropEvent(event)
        if not event.isAccepted():
            return
        
        f = event.mimeData().urls()
        for i, u in enumerate(f):
            f[i] = u.toLocalFile()

        self.setFile(f[0])
            
        #emit to signal, populate buttons below with excess files
        self.fileChanged.emit([ f[0] ])

        self.setProperty(StyleProperties.DRAG_HELD, False)
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, False)
        self.repolish(self)
        self.repolish(self._childFrame)



class NewDiscButton(DragDropButton):
    def __init__(self, parent = None):
        super(NewDiscButton, self).__init__(ButtonType.NEW_TRACK, parent)

        self._img.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addStretch(1)
        layout.addWidget(self._img)
        layout.addStretch(1)

        self.setLayout(layout)

        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.setStyleSheet(CSS_SHEET_NEWDISCBUTTON)

    def mousePressEvent(self, event):
        super(NewDiscButton, self).mousePressEvent(event)

        #new disc button only accepts music files on click
        fileTypeStr = "Music files (*.mp3; *.wav; *.ogg)"

        #allow multiple files
        f = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open file', '.', fileTypeStr)

        if(f[0] == []):
            return

        self.fileChanged.emit( f[0] )

    def dragEnterEvent(self, event):
        super(NewDiscButton, self).dragEnterEvent(event)
        if not event.isAccepted():
            return

        self.setProperty(StyleProperties.DRAG_HELD, True)
        self.repolish(self)

    def dragLeaveEvent(self, event):
        super(NewDiscButton, self).dragLeaveEvent(event)

        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.repolish(self)

    def dropEvent(self, event):
        super(NewDiscButton, self).dropEvent(event)
        if not event.isAccepted():
            return
        
        f = event.mimeData().urls()
        for i, u in enumerate(f):
            f[i] = u.toLocalFile()

        self.fileChanged.emit(f)

        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.repolish(self)



#entry in list of tracks
class DiscListEntry(QContainerFrame):
    def __init__(self, parent = None):
        super(DiscListEntry, self).__init__()

        self._parent = parent

        layout = QtWidgets.QHBoxLayout()

        #child widgets
        self._btnIcon = FileButton(ButtonType.IMAGE, self)
        self._btnTrack = FileButton(ButtonType.TRACK, self)
        self._leTitle = QFocusLineEdit("Track Title", self)
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
        self._leTitle.textChanged.connect(self.setSubtitle)

        self.setStyleSheet(CSS_SHEET_DISCENTRY)
        self._lblIName.setStyleSheet(CSS_SHEET_SUBTITLE)

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
        self._leTitle.setText(filename)

    def setSubtitle(self, title):
        internal_name = ''.join([i for i in title.lower() if i.isalpha()])
        self._lblIName.setText(internal_name)



#blank entry in list of tracks
class NewDiscEntry(QContainerFrame):
    def __init__(self, parent = None):
        super(NewDiscEntry, self).__init__()

        self._parent = parent
        
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

        self._btnAdd = NewDiscButton(self)
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
        self._thread = QThread(self)
        self._worker = GeneratePackWorker(texture_files, track_files, titles, internal_names)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.generate)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.destroyed.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

        self._btnGen.setEnabled(False)
        self._thread.finished.connect(
            lambda: self._btnGen.setEnabled(True)
        )



#worker object that generates the datapack/resourcepack in a separate QThread
class GeneratePackWorker(QObject):
    finished = pyqtSignal()
    min_prog = pyqtSignal(int)
    progress = pyqtSignal(int)
    max_prog = pyqtSignal(int)

    def __init__(self, texture_files, track_files, titles, internal_names):
        super(GeneratePackWorker, self).__init__()

        self._texture_files = texture_files
        self._track_files = track_files
        self._titles = titles
        self._internal_names = internal_names

    def generate(self):
        #total steps = validate + num track conversions + generate dp + generate rp
        self.min_prog.emit(0)
        self.progress.emit(0)
        self.max_prog.emit(len(self._track_files) + 3)

        status = 0
        progress = 0

        status = generator.validate(self._texture_files,
                                    self._track_files,
                                    self._titles,
                                    self._internal_names)
        if status > 0:
            self.finished.emit()
            return

        progress += 1
        self.progress.emit(progress)

        for i in range(len(self._track_files)):
            #wrap string in list to allow C-style passing by reference
            wrapper = [ self._track_files[i] ]
            status = generator.convert_to_ogg(wrapper,
                                              self._internal_names[i],
                                              (i == 0))
            if status > 0:
                self.finished.emit()
                return

            #extract modified string from wrapper list
            self._track_files[i] = wrapper[0]
            progress += 1
            self.progress.emit(progress)

        status = generator.generate_datapack(self._texture_files,
                                             self._track_files,
                                             self._titles,
                                             self._internal_names)
        if status > 0:
            self.finished.emit()
            return

        progress += 1
        self.progress.emit(progress)

        status = generator.generate_resourcepack(self._texture_files,
                                                 self._track_files,
                                                 self._titles,
                                                 self._internal_names)
        if status > 0:
            self.finished.emit()
            return

        progress += 1
        self.progress.emit(progress)

        print("Successfully generated datapack and resourcepack!")
        
        self.finished.emit()


