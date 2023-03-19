#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs common/shared/abstract GUI components module
#Generation tool, datapack design, and resourcepack design by link2_thepast

import os

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QSize

from src.definitions import Assets, Constants, ButtonType, Helpers, FileExt, StyleProperties



#mixin class requiring inheriting classes to use their class name as their object name
class QSetsNameFromType(QtCore.QObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setObjectName(type(self).__name__)



#mixin class that implements a "repolish" method to refresh object styles
class QRepolishMixin():
    def repolish(self, obj):
        obj.style().unpolish(obj)
        obj.style().polish(obj)



#mixin class that implements most common drag-drop functionality
class QDragDropMixin():
    def dragEnterEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        for u in event.mimeData().urls():
            u = u.toLocalFile()
            u = QtCore.QFileInfo(u).suffix()

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

        #widget may have moved away from mouse, force clear hover state
        self.setAttribute(Qt.WA_UnderMouse, False)

    def getFilesFromEvent(self, event):
        raise NotImplementedError

    def supportsFileType(self, ext):
        raise NotImplementedError

    def highlightStyling(self):
        raise NotImplementedError

    def resetStyling(self):
        raise NotImplementedError



#mixin class that implements most multi-drag-drop functionality
class QMultiDragDropMixin(QDragDropMixin):
    multiDragEnter = pyqtSignal(int, int)
    multiDragLeave = pyqtSignal(int, int)
    multiDrop = pyqtSignal(int, list)

    def dragEnterEvent(self, event):
        super().dragEnterEvent(event)
        if not event.isAccepted():
            return

        f = self.getFilesFromEvent(event)
        self.multiDragEnter.emit(self._parent.getIndex(), len(f))

    def dragLeaveEvent(self, event):
        super().dragLeaveEvent(event)

        self.multiDragLeave.emit(self._parent.getIndex(), Constants.MAX_DRAW_MULTI_DRAGDROP)

    def dropEvent(self, event):
        super().dropEvent(event)
        if not event.isAccepted():
            return

        f = self.getFilesFromEvent(event)
        self.multiDrop.emit(self._parent.getIndex(), f)

    def multiDragEnterEvent(self, initIndex, count):
        #check if this element should be highlighted
        selfIndex = self._parent.getIndex()
        if(selfIndex < initIndex):
            return
        if(selfIndex >= initIndex + min(Constants.MAX_DRAW_MULTI_DRAGDROP, count)):
            return

        dropIndex = selfIndex - initIndex

        #if so, highlight with gradient
        self.highlightStyling(dropIndex)

    def multiDragLeaveEvent(self, initIndex, count):
        #check if this element is currently highlighted
        selfIndex = self._parent.getIndex()
        if(selfIndex < initIndex):
            return
        if(selfIndex >= initIndex + min(Constants.MAX_DRAW_MULTI_DRAGDROP, count)):
            return

        #if so, remove its highlight
        self.resetStyling()

    def multiDropEvent(self, initIndex, files):
        #check if this element is currently highlighted
        #allow all files to drop, instead of restricting like outline render
        #return index of file dropped into this object, or -1 if N/A
        selfIndex = self._parent.getIndex()
        if(selfIndex < initIndex):
            return -1
        if(selfIndex >= initIndex + len(files)):
            return -1

        dropIndex = selfIndex - initIndex

        #remove highlight since files were dropped
        self.resetStyling()

        #run implementation-specific code from inheriting classes
        self.postMultiDropEvent(dropIndex, files)

    def postMultiDropEvent(self, dropIndex, files):
        raise NotImplementedError

    def highlightStyling(self, dropIndex):
        raise NotImplementedError

    def resetStyling(self):
        raise NotImplementedError



#child of QLineEdit with drag-drop text
class QDragDropLineEdit(QDragDropMixin, QRepolishMixin, QtWidgets.QLineEdit, QSetsNameFromType):
    def __init__(self, text, parent = None):
        super().__init__(text=text, parent=parent)
        self._parent = parent

        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.setProperty(StyleProperties.ALPHA, 10)

    def getFilesFromEvent(self, event):
        urls = event.mimeData().urls()

        for u in urls:
            uf = u.toLocalFile()
            uext = QtCore.QFileInfo(uf).suffix()

            if self.supportsFileType(uext):
                #parse lines from first available text file as titles
                return self.getLinesFromFile(uf)

        return []

    def getLinesFromFile(self, file):
        with open(file, 'r', encoding='utf-8') as uf:
            return list(line.replace('\n', '') for line in uf)

    def supportsFileType(self, ext):
        return ( ext in [ FileExt.TXT ] )



#child of QDragDropLineEdit with multi-drag-drop support
class QMultiDragDropLineEdit(QMultiDragDropMixin, QDragDropLineEdit):
    def postMultiDropEvent(self, dropIndex, files):
        if dropIndex < 0:
            return

        #set text from line in file
        self.setText(files[dropIndex])

    def highlightStyling(self, dropIndex):
        self.setProperty(StyleProperties.DRAG_HELD, True)
        self.setProperty(StyleProperties.ALPHA, Constants.MAX_DRAW_MULTI_DRAGDROP - dropIndex)
        self.repolish(self)

    def resetStyling(self):
        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.setProperty(StyleProperties.ALPHA, 10)
        self.repolish(self)



#child of QMultiDragDropLineEdit with text autoselect on click
class QFocusLineEdit(QMultiDragDropLineEdit):
    def focusInEvent(self, event):
        self._wasFocused = False

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if not self._wasFocused:
            self.selectAll()

        self._wasFocused = True



#child of QLabel with size hint specified
#prevents NewDiscButton icon from shrinking too much on resize event
class QImgLabel(QtWidgets.QLabel):
    def sizeHint(self):
        return QSize(52, 52)



#file selection button supporting file drag/drop
class DragDropButton(QDragDropMixin, QRepolishMixin, QtWidgets.QPushButton, QSetsNameFromType):

    fileChanged = pyqtSignal(list)

    IconDict = {
        FileExt.OGG: Assets.ICON_OGG,
        FileExt.MP3: Assets.ICON_MP3,
        FileExt.WAV: Assets.ICON_WAV
    }

    DefaultIconDict = {
        ButtonType.IMAGE:       Assets.ICON_ICON_EMPTY,
        ButtonType.PACKPNG:     Assets.ICON_PACK_EMPTY,
        ButtonType.TRACK:       Assets.ICON_TRACK_EMPTY,
        ButtonType.NEW_TRACK:   Assets.ICON_NEW_DISC
    }

    SupportedFiletypesDict = {
        ButtonType.IMAGE:       [ FileExt.PNG ],
        ButtonType.PACKPNG:     [ FileExt.PNG ],
        ButtonType.TRACK:       [ FileExt.MP3, FileExt.WAV, FileExt.OGG ],
        ButtonType.NEW_TRACK:   [ FileExt.MP3, FileExt.WAV, FileExt.OGG ]
    }

    def __init__(self, btnType = ButtonType.IMAGE, parent = None):
        super().__init__(parent=parent)

        self._parent = parent

        self._file = ''
        self._type = btnType

        if self._type == ButtonType.PACKPNG:
            if os.path.isfile('pack.png'):
                self._file = 'pack.png'

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setAcceptDrops(True)

        #icon object
        self._img = QImgLabel(self)
        self._img.setScaledContents(True)
        self.setImage(self._file)

    def sizeHint(self):
        return QSize(80, 80)

    #TODO: how to reduce the number of on resize / on show handler calls?
    #widget geometry is wrong at creation, so icon pixmap gets scaled to the wrong dimensions
    #redraw icon on resize events to ensure icon is correctly scaled
    def resizeEvent(self, event):
        event.accept()
        self.setImage(self._file)

    #also redraw icon on show event to handle cases where buttons are created without being resized after
    def showEvent(self, event):
        event.accept()
        self.setImage(self._file)

    def mousePressEvent(self, event):
        event.accept()

    def hasFile(self):
        return (self._file != None)

    def getFile(self):
        return self._file

    def setFile(self, file):
        self._file = file
        self.setImage(self._file)

    def setImage(self, file):
        f = QtCore.QFileInfo(file).suffix()

        if(f == FileExt.PNG):
            imgPath = self._file
        else:
            defaultIcon = self.DefaultIconDict.get(self._type, '')
            imgPath = self.IconDict.get(f, defaultIcon)

        if not imgPath == '':
            self._img.setPixmap(self.getScaledImage(QtGui.QPixmap(imgPath)))

    def getScaledImage(self, pixmap):
        return pixmap.scaled(self._img.frameGeometry().width(), self._img.frameGeometry().height(), Qt.KeepAspectRatio)

    def getFilesFromEvent(self, event):
        urls = event.mimeData().urls()
        f = []

        for u in urls:
            uf = u.toLocalFile()
            uext = QtCore.QFileInfo(uf).suffix()

            if self.supportsFileType(uext):
                f.append(uf)

        return sorted(f, key=Helpers.natural_keys)

    def supportsFileType(self, ext):
        return ( ext in self.SupportedFiletypesDict.get(self._type, []) )



#child of DragDropButton supporting multi-file drag-drop
class MultiDragDropButton(QMultiDragDropMixin, DragDropButton):
    def __init__(self, btnType = ButtonType.IMAGE, parent = None):
        super().__init__(btnType=btnType, parent=parent)

        #child QFrame, for CSS styling purposes
        self._childFrame = QtWidgets.QFrame()
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

        self._childFrame.setObjectName('MultiDragDropButtonFrame')

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        #set accepted file types based on button function
        if(self._type == ButtonType.IMAGE or self._type == ButtonType.PACKPNG):
            fileTypeStr = Constants.FILTER_IMAGE
        else:
            fileTypeStr = Constants.FILTER_MUSIC

        #allow user to pick one file for this button
        f = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '.', fileTypeStr)

        if(f[0] == ''):
            return

        self.setFile(f[0])

        #wrap file string in a list to match signal type
        self.fileChanged.emit([ f[0] ])

    def postMultiDropEvent(self, dropIndex, files):
        if dropIndex < 0:
            return

        #save file
        self.setFile(files[dropIndex])
        self.fileChanged.emit([ files[dropIndex] ])

    def highlightStyling(self, dropIndex):
        self.setProperty(StyleProperties.DRAG_HELD, True)
        self.setProperty(StyleProperties.ALPHA, Constants.MAX_DRAW_MULTI_DRAGDROP - dropIndex)
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, True)
        self.repolish(self)
        self.repolish(self._childFrame)

    def resetStyling(self):
        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.setProperty(StyleProperties.ALPHA, 10)
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, False)
        self.repolish(self)
        self.repolish(self._childFrame)


