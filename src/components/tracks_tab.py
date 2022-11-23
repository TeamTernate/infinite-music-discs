#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs tracks-tab-specific GUI components module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QSize

from src.definitions import Assets, Constants, ButtonType, Helpers, StyleProperties
from src.components.common import QSetsNameFromType, QFocusLineEdit, DragDropButton, FileButton



#child of QLabel with size hint specified
#prevents tracks with long subtitles from exceeding window width
class QSubtitleLabel(QtWidgets.QLabel):
    def sizeHint(self):
        return QSize(10, 10)



#button for removing a track list element
class DeleteButton(QtWidgets.QPushButton, QSetsNameFromType):
    def __init__(self, parent = None):
        super().__init__(parent=parent)

    def sizeHint(self):
        return QSize(25, 25)

    def clearHoverState(self):
        #button may have moved away from mouse, force clear hover state
        self.setAttribute(Qt.WA_UnderMouse, False)
        self.repaint()



#button for reordering track list elements
class ArrowButton(QtWidgets.QPushButton, QSetsNameFromType):
    pressed = pyqtSignal(int)

    #use dictionary to choose appropriate icon, based on button type and disabled status
    ImageFromButtonTypeDict = {
        (ButtonType.ARROW_UP, True):    Assets.ICON_ARROW_UP_DIS,
        (ButtonType.ARROW_UP, False):   Assets.ICON_ARROW_UP,
        (ButtonType.ARROW_DOWN, True):  Assets.ICON_ARROW_DOWN_DIS,
        (ButtonType.ARROW_DOWN, False): Assets.ICON_ARROW_DOWN
    }

    def __init__(self, btnType = ButtonType.ARROW_UP, parent = None):
        super().__init__(parent=parent)

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

    def sizeHint(self):
        return QSize(25, 25)

    def mousePressEvent(self, event):
        event.accept()

        index = self._parent.getIndex()
        self.pressed.emit(index)

    def setImage(self, btnType, disabled):
        img = self.ImageFromButtonTypeDict[ (btnType, disabled) ]
        self._img.setPixmap(QtGui.QPixmap(img))

    def setDisabled(self, disabled):
        super().setDisabled(disabled)
        self.setImage(self._type, disabled)

        #button may have moved away from mouse, force clear hover state
        self.setAttribute(Qt.WA_UnderMouse, False)



class NewDiscButton(DragDropButton, QSetsNameFromType):
    def __init__(self, parent = None):
        super().__init__(btnType=ButtonType.NEW_TRACK, parent=parent)

        self._img.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.setProperty(StyleProperties.DRAG_HELD, False)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addStretch(1)
        layout.addWidget(self._img)
        layout.addStretch(1)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        #new disc button only accepts music files on click
        fileTypeStr = Constants.FILTER_MUSIC

        #allow user to pick multiple files using dialog
        f = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open file', '.', fileTypeStr)

        if(f[0] == []):
            return

        #return file list directly, signal is of type list
        self.fileChanged.emit( f[0] )

    def dragEnterEvent(self, event):
        super().dragEnterEvent(event)
        if not event.isAccepted():
            return

        self.highlightStyling()

    def dragLeaveEvent(self, event):
        super().dragLeaveEvent(event)
        self.resetStyling()

    def dropEvent(self, event):
        super().dropEvent(event)
        if not event.isAccepted():
            return

        f = self.getFilesFromEvent(event)
        self.fileChanged.emit(f)
        self.resetStyling()

    def highlightStyling(self):
        self.setProperty(StyleProperties.DRAG_HELD, True)
        self.repolish(self)

    def resetStyling(self):
        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.repolish(self)



#abstract class containing common code between DiscList entries
#inherited by DiscListEntry and NewDiscEntry
class AbstractDiscListEntry(QtWidgets.QFrame, QSetsNameFromType):
    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self._parent = parent

        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def sizeHint(self):
        return QSize(350, 87)

    def heightForWidth(self, width):
        return width * 0.375

#TODO: move some parsing / helper functions to Helpers() class
#TODO: create data subclass to store magic numbers by name? reduce confusing magic numbers?
#entry in list of tracks
class DiscListEntry(AbstractDiscListEntry):
    def __init__(self, parent = None):
        super().__init__(parent=parent)

        layout = QtWidgets.QHBoxLayout()

        #child widgets
        self._btnIcon = FileButton(ButtonType.IMAGE, self)
        self._btnTrack = FileButton(ButtonType.TRACK, self)
        self._leTitle = QFocusLineEdit("Track Title", self)
        self._lblIName = QSubtitleLabel("internal name", self)
        self._btnDelete = DeleteButton(self)
        self._btnUpArrow = ArrowButton(ButtonType.ARROW_UP, self)
        self._btnDownArrow = ArrowButton(ButtonType.ARROW_DOWN, self)

        self._leTitle.setMaxLength(Constants.LINE_EDIT_MAX_CHARS)
        self._leTitle.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred))
        self._lblIName.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred))

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

        #scroll area to prevent internal name label from resizing DiscListEntry
        iNameScrollArea = QtWidgets.QScrollArea(self)
        iNameScrollArea.setWidget(self._lblIName)
        iNameScrollArea.setWidgetResizable(True)
        iNameScrollArea.setMinimumHeight(self._lblIName.height())
        iNameScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        iNameScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        iNameScrollArea.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum))

        #container layouts for track title, internal name label, and track delete button
        ulLayout = QtWidgets.QHBoxLayout()
        ulLayout.addWidget(iNameScrollArea, 1)
        ulLayout.addWidget(self._btnDelete, 0, Qt.AlignRight)
        ulLayout.setSpacing(10)
        ulLayout.setContentsMargins(0, 10, 0, 0)

        txtLayout = QtWidgets.QVBoxLayout()
        txtLayout.addWidget(self._leTitle, 1)
        txtLayout.addLayout(ulLayout)
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

        self._leTitle.multiDragEnter.connect(self._parent.title_multiDragEnter)
        self._leTitle.multiDragLeave.connect(self._parent.title_multiDragLeave)
        self._leTitle.multiDrop.connect(self._parent.title_multiDrop)
        self._parent.title_multiDragEnter.connect(self._leTitle.multiDragEnterEvent)
        self._parent.title_multiDragLeave.connect(self._leTitle.multiDragLeaveEvent)
        self._parent.title_multiDrop.connect(self._leTitle.multiDropEvent)

        #bind other signals
        self._btnDelete.clicked.connect(self.deleteSelf)
        self._btnTrack.fileChanged.connect(self.setTitle)
        self._leTitle.textChanged.connect(self.setSubtitle)

        self._btnIcon.setObjectName('ImageButton')
        self._btnTrack.setObjectName('TrackButton')
        self._leTitle.setObjectName('TitleLineEdit')
        self._lblIName.setObjectName('INameLabel')
        self._btnDelete.setObjectName('DeleteButton')
        self._btnUpArrow.setObjectName('ArrowUp')
        self._btnDownArrow.setObjectName('ArrowDown')

    def leaveEvent(self, event):
        self._btnDelete.clearHoverState()

    def listReorderEvent(self, count):
        index = self.getIndex()
        self._btnUpArrow.setDisabled( index <= 0 )
        self._btnDownArrow.setDisabled( index >= count-1 )

    def deleteSelf(self):
        self._parent.removeDiscEntry(self.getIndex())

    #TODO: too brittle, implement getIndex in parent
    def getIndex(self):
        return self._parent._childLayout.indexOf(self)

    #TODO: return dictionary / dataclass so entries are named?
    #TODO: inner class factory for generating "entry" object?
    def getEntry(self):
        return [self._btnIcon.getFile(), self._btnTrack.getFile(), self._leTitle.text(), self._lblIName.text()]

    def setEntry(self, fIcon, fTrack, title):
        self._btnIcon.setFile(fIcon)
        self._btnTrack.setFile(fTrack)

        self.setTitle([ fTrack ])

    def setTitle(self, fFileList):
        #TODO: using completeBaseName here breaks if there are "." in the track name
        title = QtCore.QFileInfo(fFileList[0]).completeBaseName()
        self._leTitle.setText(title)

    def setSubtitle(self, title):
        self._lblIName.setText( Helpers.to_internal_name(title) )



#blank entry in list of tracks
class NewDiscEntry(AbstractDiscListEntry):
    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self._btnAdd = NewDiscButton(self)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._btnAdd, 1)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 0, 5, 0)

        self.setLayout(layout)



#TODO: create AbstractList with standard setup for DiscList and SettingsList?
#list of tracks
class DiscList(QtWidgets.QWidget, QSetsNameFromType):

    reordered = pyqtSignal(int)

    icon_multiDragEnter = pyqtSignal(int, int)
    icon_multiDragLeave = pyqtSignal(int, int)
    icon_multiDrop = pyqtSignal(int, list)

    track_multiDragEnter = pyqtSignal(int, int)
    track_multiDragLeave = pyqtSignal(int, int)
    track_multiDrop = pyqtSignal(int, list)

    title_multiDragEnter = pyqtSignal(int, int)
    title_multiDragLeave = pyqtSignal(int, int)
    title_multiDrop = pyqtSignal(int, list)

    def __init__(self, parent = None):
        super().__init__(parent=parent)

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
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        #layout, contains scroll area
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scrollArea)

        self.setLayout(layout)

        self.icon_multiDrop.connect(self.addExcessEntries)
        self.track_multiDrop.connect(self.addExcessEntries)
        self.title_multiDrop.connect(self.addExcessEntries)

        widget.setObjectName('DiscListChildWidget')
        scrollArea.setObjectName('DiscListScrollArea')

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

    def removeDiscEntry(self, index):
        w = self._childLayout.itemAt(index).widget()
        self._childLayout.removeWidget(w)
        w.deleteLater()
        w = None

        #trigger reorder event
        self.reordered.emit(self.getNumDiscEntries())


