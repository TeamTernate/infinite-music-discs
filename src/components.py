#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack GUI components module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from PyQt5.QtCore import Qt, QFileInfo, QSize, QObject, QThread, pyqtSignal
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from enum import Enum

import os
import generator

#typedefs and constants
class ButtonType(Enum):
    IMAGE = 1
    TRACK = 2
    NEW_TRACK = 3
    ARROW_UP = 4
    ARROW_DOWN = 5
    PACKPNG = 6

class SettingType(Enum):
    PACKPNG = 1
    CHECK = 2
    RADIO = 3
    DROPDOWN = 4

class FileExt():
    PNG = 'png'
    MP3 = 'mp3'
    WAV = 'wav'
    OGG = 'ogg'

class Assets():
    ICON_ICON_EMPTY =       '../data/image-empty.png'
    ICON_TRACK_EMPTY =      '../data/track-empty.png'
    ICON_PACK_EMPTY =       '../data/pack-empty.png'
    ICON_NEW_DISC =         '../data/new-disc.png'
    ICON_MP3 =              '../data/track-mp3.png'
    ICON_WAV =              '../data/track-wav.png'
    ICON_OGG =              '../data/track-ogg.png'
    ICON_ARROW_UP =         '../data/arrow-up.png'
    ICON_ARROW_DOWN =       '../data/arrow-down.png'
    ICON_ARROW_UP_DIS =     '../data/arrow-up-disabled.png'
    ICON_ARROW_DOWN_DIS =   '../data/arrow-down-disabled.png'

class StyleProperties():
    DRAG_HELD = 'drag_held'
    ALPHA =     'alpha'
    DISABLED =  'disabled'

MAX_DRAW_MULTI_DRAGDROP = 10

CSS_SHEET_ARROWBUTTON = """
ArrowButton {
    border: 0;
    background-color: rgb(48, 48, 48);
}

ArrowButton:hover {
    background-color: rgb(96, 96, 96);
}
"""

CSS_SHEET_TRACKNAME = """
QLineEdit {
    padding-left: 10px;
    padding-right: 10px;

    color: lightgray;
    font-size: 16px;
    border-radius: 4px;

    background-color: rgb(32, 32, 32);
}

QLineEdit:focus {
    color: white;
    border: 1px solid lightgray;
}

QLabel {
    color: gray;
    font-style: italic;
}
"""

CSS_SHEET_DRAGDROPBUTTON = """
DragDropButton {
    background-color: rgb(48, 48, 48);
    border: 5px solid rgb(48, 48, 48);
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
    border-top: 4px solid qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 black, stop:1 rgba(0,0,0,0));
    border-bottom: 3px solid qlineargradient(x1:0, y1:1, x2:0, y2:0, stop:0 rgb(32,32,32), stop:1 rgba(0,0,0,0));
    border-left: 4px solid qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 black, stop:1 rgba(0,0,0,0));
    border-right: 3px solid qlineargradient(x1:1, y1:0, x2:0, y2:0, stop:0 rgb(32,32,32), stop:1 rgba(0,0,0,0));

    background-color: rgb(32, 32, 32);
}

QContainerFrame:hover[drag_held="true"] {
    background-color: rgb(72, 72, 72);
}

QContainerFrame:hover {
    background-color: rgb(72, 72, 72);
}
"""

CSS_SHEET_NEWDISCBUTTON = """
NewDiscButton {
    border-top: 4px solid qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 black, stop:1 rgba(0,0,0,0));
    border-bottom: 3px solid qlineargradient(x1:0, y1:1, x2:0, y2:0, stop:0 rgb(24,24,24), stop:1 rgba(0,0,0,0));
    border-left: 4px solid qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 black, stop:1 rgba(0,0,0,0));
    border-right: 3px solid qlineargradient(x1:1, y1:0, x2:0, y2:0, stop:0 rgb(24,24,24), stop:1 rgba(0,0,0,0));

    font-size: 48px;
    color: gray;
    background-color: rgb(32, 32, 32);
}

NewDiscButton:hover {
    color:lightgray;
    background-color: rgb(72, 72, 72);
}

NewDiscButton:hover[drag_held="true"] {
}
"""

CSS_SHEET_DISCENTRY = """
DiscListEntry {
    padding: 1px;
    border-bottom: 2px solid rgb(72, 72, 72);
    background-color: rgb(48, 48, 48);
}
"""

CSS_SHEET_NEWENTRY = """
NewDiscEntry {
    padding: 5px;
    background-color: rgb(48, 48, 48);
}
"""

CSS_SHEET_DISCLIST = """
QScrollArea {
    padding: 0;
    border: 0;
}

#ChildWidget {
    background-color: rgb(48, 48, 48);
}
"""

CSS_SHEET_SETTINGS = """
SettingsListEntry#PACKPNG {
    border: 0;
    /* border-bottom: 4px solid qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgb(32,32,32), stop:0.8 rgba(0,0,0,0), stop:1 rgb(32,32,32)); */
    border-bottom: 2px solid rgb(72, 72, 72);
}

QLabel#Label {
    color: lightgray;
    font-weight: normal;
    font-size: 16px;
}

QScrollArea {
    padding: 0;
    border: 0;
}

#ChildWidget {
    background-color: rgb(48, 48, 48);
}
"""

CSS_SHEET_TABS = """
QTabWidget::pane {
    padding: 0;
    border: 0;
    background-color: rgb(32, 32, 32);
}

QTabWidget::tab-bar {
}

QTabBar {
    padding: 0;
    border: 0;
    background-color: rgb(32, 32, 32);
}

QTabBar::tab {
    font-weight: normal;
    font-size: 16px;
    color: lightgray;
    background-color: rgb(32, 32, 32);
}

QTabBar::tab:selected {
    font-weight: bold;
    color: white;
}

QTabBar::tab:hover {
    color: white;
}
"""

CSS_SHEET_SCROLLBAR = """
QScrollBar:vertical {
    padding: 0;
    border: 0;
    background-color: rgb(32, 32, 32);
}

QScrollBar::handle:vertical {
    background-color: rgb(72, 72, 72);
    min-height: 0px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgb(96, 96, 96);
}

QScrollBar::add-line:vertical {
    border: none;
    background: none;
    width: 0px;
    height: 0px;
}

QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    width: 0px;
    height: 0px;
}
"""

CSS_SHEET_CENTRAL = """
CentralWidget {
    padding: 0;
    border: 0;
}

DiscList {
    background-color: rgb(48, 48, 48);
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

        self._img = QtWidgets.QLabel(self)
        self.setImage(self._type, False)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._img)

        self.setLayout(layout)
        self.setStyleSheet(CSS_SHEET_ARROWBUTTON)

    def sizeHint(self):
        return QSize(25, 25)

    def mousePressEvent(self, event):
        event.accept()

        index = self._parent.getIndex()
        self.pressed.emit(index)

    def setImage(self, btnType, disabled):
        if(btnType == ButtonType.ARROW_UP):
            if disabled:
                self._img.setPixmap(QtGui.QPixmap(Assets.ICON_ARROW_UP_DIS))
            else:
                self._img.setPixmap(QtGui.QPixmap(Assets.ICON_ARROW_UP))
        else:
            if disabled:
                self._img.setPixmap(QtGui.QPixmap(Assets.ICON_ARROW_DOWN_DIS))
            else:
                self._img.setPixmap(QtGui.QPixmap(Assets.ICON_ARROW_DOWN))

    def setDisabled(self, disabled):
        super(ArrowButton, self).setDisabled(disabled)
        self.setImage(self._type, disabled)

        #button may have moved away from mouse, force clear hover state
        self.setAttribute(Qt.WA_UnderMouse, False)



#file selection button supporting file drag/drop
class DragDropButton(QtWidgets.QPushButton):
    
    fileChanged = pyqtSignal(list)

    def __init__(self, btnType = ButtonType.IMAGE, parent = None):
        super(DragDropButton, self).__init__(parent)

        self._parent = parent

        self._file = ''
        self._type = btnType

        if self._type == ButtonType.PACKPNG:
            if os.path.isfile('pack.png'):
                self._file = 'pack.png'

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

            if(self.supportsFileType(u)):
                event.accept()
                return

        event.ignore()

    def dragLeaveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

        #button may have moved away from mouse, force clear hover state
        self.setAttribute(Qt.WA_UnderMouse, False)

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
        elif(self._type == ButtonType.PACKPNG):
            imgPath = assetDict.get(f, Assets.ICON_PACK_EMPTY)
        elif(self._type == ButtonType.NEW_TRACK):
            self.setText('+')
            #imgPath = assetDict.get(f, Assets.ICON_NEW_DISC)
        else:
            pass

        self._img.setPixmap(self.getScaledImage(QtGui.QPixmap(imgPath)))

    def getScaledImage(self, pixmap):
        return pixmap.scaled(self._img.frameGeometry().width(), self._img.frameGeometry().height(), Qt.KeepAspectRatio)

    def getFilesFromEvent(self, event):
        urls = event.mimeData().urls()
        f = []

        for u in urls:
            uf = u.toLocalFile()
            uext = QFileInfo(uf).completeSuffix()

            if self.supportsFileType(uext):
                f.append(uf)

        return f

    def supportsFileType(self, ext):
        if(self._type == ButtonType.IMAGE):
            return ( ext in [ FileExt.PNG ] )
        if(self._type == ButtonType.PACKPNG):
            return ( ext in [ FileExt.PNG ] )
        if(self._type == ButtonType.TRACK):
            return ( ext in [ FileExt.MP3, FileExt.WAV, FileExt.OGG ] )
        if(self._type == ButtonType.NEW_TRACK):
            return ( ext in [ FileExt.MP3, FileExt.WAV, FileExt.OGG, FileExt.PNG ] )



class FileButton(DragDropButton):

    multiDragEnter = pyqtSignal(int, int)
    multiDragLeave = pyqtSignal(int, int)
    multiDrop = pyqtSignal(int, list)

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
        if(self._type == ButtonType.IMAGE or self._type == ButtonType.PACKPNG):
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

        f = self.getFilesFromEvent(event)
        self.multiDragEnter.emit(self._parent.getIndex(), len(f))

    def dragLeaveEvent(self, event):
        super(FileButton, self).dragLeaveEvent(event)

        self.multiDragLeave.emit(self._parent.getIndex(), MAX_DRAW_MULTI_DRAGDROP)

    def dropEvent(self, event):
        super(FileButton, self).dropEvent(event)
        if not event.isAccepted():
            return

        f = self.getFilesFromEvent(event)
        self.multiDrop.emit(self._parent.getIndex(), f)

    def multiDragEnterEvent(self, initIndex, count):
        #check if this element should be highlighted
        selfIndex = self._parent.getIndex()
        if(selfIndex < initIndex):
            return
        if(selfIndex >= initIndex + min(MAX_DRAW_MULTI_DRAGDROP, count)):
            return

        #update styling
        self.setProperty(StyleProperties.DRAG_HELD, True)
        self.setProperty(StyleProperties.ALPHA, MAX_DRAW_MULTI_DRAGDROP - (selfIndex - initIndex))
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, True)
        self.repolish(self)
        self.repolish(self._childFrame)

    def multiDragLeaveEvent(self, initIndex, count):
        #check if this element should be highlighted
        selfIndex = self._parent.getIndex()
        if(selfIndex < initIndex):
            return
        if(selfIndex >= initIndex + min(MAX_DRAW_MULTI_DRAGDROP, count)):
            return

        #reset styling
        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.setProperty(StyleProperties.ALPHA, 10)
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, False)
        self.repolish(self)
        self.repolish(self._childFrame)

    def multiDropEvent(self, initIndex, files):
        #check if this element should be highlighted
        #   allow all files to drop, instead of restricting like outline render
        selfIndex = self._parent.getIndex()
        if(selfIndex < initIndex):
            return
        if(selfIndex >= initIndex + len(files)):
            return

        #save file
        deltaIndex = selfIndex - initIndex

        self.setFile(files[deltaIndex])
        self.fileChanged.emit([ files[deltaIndex] ])

        #reset styling
        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.setProperty(StyleProperties.ALPHA, 10)
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
        self._leTitle.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred))
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

        #bind signals for multi drag-drop operation
        self._btnIcon.multiDragEnter.connect(self._parent.icon_multiDragEnter)
        self._btnIcon.multiDragLeave.connect(self._parent.icon_multiDragLeave)
        self._btnIcon.multiDrop.connect(self._parent.icon_multiDrop)
        self._parent.icon_multiDragEnter.connect(self._btnIcon.multiDragEnterEvent)
        self._parent.icon_multiDragLeave.connect(self._btnIcon.multiDragLeaveEvent)
        self._parent.icon_multiDrop.connect(self._btnIcon.multiDropEvent)

        self._btnTrack.multiDragEnter.connect(self._parent.track_multiDragEnter)
        self._btnTrack.multiDragLeave.connect(self._parent.track_multiDragLeave)
        self._btnTrack.multiDrop.connect(self._parent.track_multiDrop)
        self._parent.track_multiDragEnter.connect(self._btnTrack.multiDragEnterEvent)
        self._parent.track_multiDragLeave.connect(self._btnTrack.multiDragLeaveEvent)
        self._parent.track_multiDrop.connect(self._btnTrack.multiDropEvent)

        #bind other signals
        self._btnTrack.fileChanged.connect(self.setTitle)
        self._leTitle.textChanged.connect(self.setSubtitle)

        self.setStyleSheet(CSS_SHEET_DISCENTRY)
        self._leTitle.setStyleSheet(CSS_SHEET_TRACKNAME)
        self._lblIName.setStyleSheet(CSS_SHEET_TRACKNAME)

    def sizeHint(self):
        return QSize(350, 87.5)

    def listReorderEvent(self, count):
        index = self.getIndex()
        
        if(index <= 0):
            self._btnUpArrow.setDisabled(True)
        else:
            self._btnUpArrow.setDisabled(False)

        if(index >= count-1):
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

    icon_multiDragEnter = pyqtSignal(int, int)
    icon_multiDragLeave = pyqtSignal(int, int)
    icon_multiDrop = pyqtSignal(int, list)

    track_multiDragEnter = pyqtSignal(int, int)
    track_multiDragLeave = pyqtSignal(int, int)
    track_multiDrop = pyqtSignal(int, list)

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
        widget.setObjectName("ChildWidget")
        widget.setLayout(self._childLayout)

        #scroll area, contains child widget and makes child widget scrollable
        scrollArea = QtWidgets.QScrollArea(self)
        scrollArea.setWidget(widget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setStyleSheet(CSS_SHEET_SCROLLBAR)

        #layout, contains scroll area
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

        self.setLayout(layout)

        self.setStyleSheet(CSS_SHEET_DISCLIST)

        self.icon_multiDrop.connect(self.addExcessEntries)
        self.track_multiDrop.connect(self.addExcessEntries)

    def discMoveUpEvent(self, index):
        if(index == 0):
            pass
        
        #move entry up
        tmpEntry = self._childLayout.itemAt(index).widget()
        self._childLayout.removeWidget(tmpEntry)
        self._childLayout.insertWidget(index-1, tmpEntry, 0, Qt.AlignTop)

        #trigger reorder event
        self.reordered.emit(self.getNumDiscEntries())

    def discMoveDownEvent(self, index):
        if(index == self.getNumDiscEntries()):
            pass

        #move entry down
        tmpEntry = self._childLayout.itemAt(index).widget()
        self._childLayout.removeWidget(tmpEntry)
        self._childLayout.insertWidget(index+1, tmpEntry, 0, Qt.AlignTop)

        #trigger reorder event
        self.reordered.emit(self.getNumDiscEntries())

    #get all stored track data
    def getDiscEntries(self):
        entries = []
        
        for i in range(self._childLayout.count()):
            e = self._childLayout.itemAt(i).widget()

            if(type(e) == DiscListEntry):
                entries.append(e.getEntry())

        return entries

    def getNumDiscEntries(self):
        return self._childLayout.count()-2

    #insert a new track object into the list of tracks
    def addDiscEntry(self, fIcon, fTrack, title):
        #add new entry
        tmpEntry = DiscListEntry(self)
        tmpEntry.setEntry(fIcon, fTrack, title)

        #insert into list
        self._childLayout.insertWidget(self.getNumDiscEntries(), tmpEntry, 0, Qt.AlignTop)

        #bind button events
        tmpEntry._btnUpArrow.pressed.connect(self.discMoveUpEvent)
        tmpEntry._btnDownArrow.pressed.connect(self.discMoveDownEvent)

        #trigger reorder event
        self.reordered.connect(tmpEntry.listReorderEvent)
        self.reordered.emit(self.getNumDiscEntries())

    #add multiple track objects to the list of tracks
    def addDiscEntries(self, fTrackList):
        for f in fTrackList:
            if '.png' in f:
                self.addDiscEntry(f, '', "New Track")
            else:
                self.addDiscEntry('', f, "New Track")

    #add remaining track objects after a multi drag-drop 
    def addExcessEntries(self, initIndex, fTrackList):
        numTracks = len(fTrackList)
        numEntries = self.getNumDiscEntries()
        
        remainingTracks = numTracks - (numEntries - initIndex)
        remainingIndex = numTracks - remainingTracks

        if(remainingTracks > 0):
            self.addDiscEntries(fTrackList[remainingIndex:])



class SettingsSelector(QtWidgets.QWidget):
    def __init__(self, settingType = SettingType.PACKPNG, params = None, parent = None):
        super(SettingsSelector, self).__init__(parent)

        self._parent = parent
        self._type = settingType

        if(self._type == SettingType.PACKPNG):
            self._parent.setObjectName("PACKPNG")
            self._widget = FileButton(ButtonType.PACKPNG, parent)
            self._widget.multiDragEnter.connect(self._widget.multiDragEnterEvent)
            self._widget.multiDragLeave.connect(self._widget.multiDragLeaveEvent)
            self._widget.multiDrop.connect(self._widget.multiDropEvent)

        elif(self._type == SettingType.CHECK):
            self._parent.setObjectName("CHECK")
            self._widget = QtWidgets.QCheckBox(self)

        elif(self._type == SettingType.RADIO):
            self._parent.setObjectName("RADIO")
            self._widget = QtWidgets.QRadioButton(self)

        elif(self._type == SettingType.DROPDOWN):
            self._parent.setObjectName("DROPDOWN")
            self._widget = QtWidgets.QComboBox(self)

            if not params == None:
                self._widget.addItems(params)

    def getWidget(self):
        return self._widget

    def getValue(self):
        if(self._type == SettingType.PACKPNG):
            return self._widget.getFile()
        elif(self._type == SettingType.CHECK):
            return self._widget.isChecked()
        elif(self._type == SettingType.RADIO):
            return self._widget.isChecked()
        elif(self._type == SettingType.DROPDOWN):
            return self._widget.currentText()



class SettingsListEntry(QContainerFrame):
    def __init__(self, key, label, settingType = SettingType.PACKPNG, params = None, parent = None):
        super(SettingsListEntry, self).__init__(parent)

        self._parent = parent
        self._key = key

        self._label = QtWidgets.QLabel(label)
        self._selector = SettingsSelector(settingType, params, self)

        self._label.setObjectName("Label")

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(5, 5, 5, 5)

        if not settingType == SettingType.PACKPNG:
            layout.setContentsMargins(50, -1, -1, -1)

        layout.addWidget(self._selector.getWidget())
        layout.addWidget(self._label)
        layout.addStretch(1)

        self.setLayout(layout)

    def getIndex(self):
        return 0

    def getKeyValue(self):
        return {self._key : self._selector.getValue()}



class SettingsList(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(SettingsList, self).__init__(parent)

        self._parent = parent

        #child layout, contains settings entries
        self._childLayout = QtWidgets.QVBoxLayout()
        self._childLayout.setSpacing(0)
        self._childLayout.setContentsMargins(1, 1, 1, 1)

        self._childLayout.addWidget(SettingsListEntry('pack', "Pack icon (pack.png)", SettingType.PACKPNG))
        self._childLayout.addWidget(SettingsListEntry('version', "Game version", SettingType.DROPDOWN, ['1.17', '1.16']))
        self._childLayout.addWidget(SettingsListEntry('zip', "Generate pack as .zip", SettingType.CHECK))
        self._childLayout.addWidget(SettingsListEntry('mix_mono', "Mix stereo tracks to mono", SettingType.CHECK))
        self._childLayout.addWidget(SettingsListEntry('keep_tmp', "Keep intermediate converted files", SettingType.CHECK))
        self._childLayout.addStretch()

        #child widget, contains child layout
        widget = QtWidgets.QWidget()
        widget.setObjectName("ChildWidget")
        widget.setLayout(self._childLayout)

        #scroll area, contains child widget and makes child widget scrollable
        scrollArea = QtWidgets.QScrollArea(self)
        scrollArea.setWidget(widget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollArea.setStyleSheet(CSS_SHEET_SCROLLBAR)

        #layout, contains scroll area
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

        self.setLayout(layout)

        self.setStyleSheet(CSS_SHEET_SETTINGS)

    def getUserSettings(self):
        settingsDict = {}
        for i in range(self._childLayout.count()):
            e = self._childLayout.itemAt(i).widget()

            if(type(e) == SettingsListEntry):
                settingsDict.update(e.getKeyValue())

        return settingsDict



#primary container widget
class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(CentralWidget, self).__init__()

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        #list of music disc tracks
        self._discList = DiscList()
        self._discList.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)

        #generation settings
        self._settingsList = SettingsList()
        self._settingsList.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)

        #tabs to switch between track list and settings
        tabs = QtWidgets.QTabWidget()
        tabs.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        tabs.setStyleSheet(CSS_SHEET_TABS)

        #set tabs background color
        tabs.setAutoFillBackground(True)
        palette = tabs.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(32, 32, 32))
        tabs.setPalette(palette)

        tabs.addTab(self._discList, "    Tracks    ")
        tabs.addTab(self._settingsList, "    Settings    ")
        layout.addWidget(tabs, 0)

        #button to generate datapack/resourcepack
        self._btnGen = GenerateButton()
        self._btnGen.generate.connect(self.generatePacks)
        layout.addWidget(self._btnGen, 0, Qt.AlignBottom)

        self.setLayout(layout)

        self.setStyleSheet(CSS_SHEET_CENTRAL)

    def generatePacks(self):
        settings = self._settingsList.getUserSettings()
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
        self._worker = GeneratePackWorker(settings, texture_files, track_files, titles, internal_names)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.generate)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.destroyed.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._btnGen.setEnabled(False)
        self._thread.finished.connect(
            lambda: self._btnGen.setEnabled(True)
        )

        self._thread.start()



#worker object that generates the datapack/resourcepack in a separate QThread
class GeneratePackWorker(QObject):
    finished = pyqtSignal()
    min_prog = pyqtSignal(int)
    progress = pyqtSignal(int)
    max_prog = pyqtSignal(int)

    def __init__(self, settings, texture_files, track_files, titles, internal_names):
        super(GeneratePackWorker, self).__init__()

        self._settings = settings
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
                                    self._internal_names,
                                    self._settings['pack'])
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
                                             self._internal_names,
                                             self._settings)
        if status > 0:
            self.finished.emit()
            return

        progress += 1
        self.progress.emit(progress)

        status = generator.generate_resourcepack(self._texture_files,
                                                 self._track_files,
                                                 self._titles,
                                                 self._internal_names,
                                                 self._settings)
        if status > 0:
            self.finished.emit()
            return

        progress += 1
        self.progress.emit(progress)

        print("Successfully generated datapack and resourcepack!")
        
        self.finished.emit()


