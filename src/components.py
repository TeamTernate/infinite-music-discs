#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack GUI components module
#Generation tool, datapack design, and resourcepack design by link2_thepast

import os
import re

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize

from src import generator
from src.generator import Status
from src.definitions import Assets, Constants, ButtonType, SettingType, FileExt, StyleProperties
from src.definitions import StatusMessageDict, DigitNameDict, CSS_STYLESHEET



#Child of QLineEdit with text autoselect on click
class QFocusLineEdit(QtWidgets.QLineEdit):
    def focusInEvent(self, event):
        self._wasFocused = False

    def mousePressEvent(self, event):
        super(QFocusLineEdit, self).mousePressEvent(event)

        if not self._wasFocused:
            self.selectAll()

        self._wasFocused = True


#TODO: make an abstract button with all helper functions so all buttons can inherit

#button for generating datapack/resourcepack
class GenerateButton(QtWidgets.QPushButton):

    BD_OUTER_WIDTH = 2
    BD_TOP_WIDTH = 4
    BD_SIDE_WIDTH = 5

    BD_TOP_FULL_WIDTH = BD_OUTER_WIDTH + BD_TOP_WIDTH
    BD_SIDE_FULL_WIDTH = BD_OUTER_WIDTH + BD_SIDE_WIDTH

    REGEX_CAPTURE = 'GenerateButton(\[.*?\])?\s*?\{(.*?)\}'
    REGEX_CAPTURE_TAG = '\[(.*?)='
    REGEX_CLEAN_WHITESPACE = '\n|\t| '
    REGEX_RGB = 'rgb\((.*?)\)'

    generate = pyqtSignal()
    setCurrentIndex = pyqtSignal(int)

    def __init__(self, parent = None):
        super(GenerateButton, self).__init__()

        self._parent = parent

        #initialize default state
        self.setProperty(StyleProperties.HOVER, False)
        self.setProperty(StyleProperties.PRESSED, False)
        self.setProperty(StyleProperties.DISABLED, False)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        #load custom font
        font_id = QtGui.QFontDatabase.addApplicationFont(Assets.FONT_MC_LARGE)
        font_str = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
        self._font = QtGui.QFont(font_str)

        #create button text and progress bar
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setOffset(0, 3)

        self._label = QtWidgets.QLabel("Generate", self)
        self._label.setAlignment(Qt.AlignHCenter)
        self._label.setGraphicsEffect(shadow)
        self._label.setFont(self._font)

        self._progress = QtWidgets.QProgressBar(self)
        self._progress.setAlignment(Qt.AlignHCenter)
        self._progress.setTextVisible(False)

        #container widgets and layouts
        lytLabel = QtWidgets.QVBoxLayout()
        lytLabel.setContentsMargins(0, 0, 0, 10)
        lytLabel.addStretch()
        lytLabel.addWidget(self._label)
        lytLabel.addStretch()
        wgtLabel = QtWidgets.QFrame(self)
        wgtLabel.setLayout(lytLabel)

        lytProgress = QtWidgets.QVBoxLayout()
        lytProgress.setContentsMargins(15, 0, 15, 0)
        lytProgress.addStretch()
        lytProgress.addWidget(self._progress)
        lytProgress.addStretch()
        wgtProgress = QtWidgets.QFrame(self)
        wgtProgress.setLayout(lytProgress)

        layout = QtWidgets.QStackedLayout()
        layout.addWidget(wgtLabel)
        layout.addWidget(wgtProgress)
        self.setLayout(layout)

        self.setCurrentIndex.connect(layout.setCurrentIndex)

        self.setObjectName('GenerateButton')
        self._label.setObjectName('GenLabel')
        self._progress.setObjectName('GenProgress')

        self.setStyleSheet(CSS_STYLESHEET)
        self._styleDict = self.getStyleSheetDict()

    def sizeHint(self):
        return QSize(350, 66)

    def mousePressEvent(self, event):
        event.accept()
        self.setPropertyComplete(StyleProperties.PRESSED, True)

    def mouseReleaseEvent(self, event):
        event.accept()
        self.setPropertyComplete(StyleProperties.PRESSED, False)
        self.generate.emit()

    def enterEvent(self, event):
        event.accept()
        self.setPropertyComplete(StyleProperties.HOVER, True)

    def leaveEvent(self, event):
        event.accept()
        self.setPropertyComplete(StyleProperties.PRESSED, False)
        self.setPropertyComplete(StyleProperties.HOVER, False)

    def changeEvent(self, event):
        event.accept()

        if event.type() == QtCore.QEvent.EnabledChange:
            self.setPropertyComplete(StyleProperties.DISABLED, not self.isEnabled() )

            #disabled -> enabled after pack generation
            if self.isEnabled():
                #do exit logic
                pass
            else:
                #do entry logic
                pass

    def paintEvent(self, event):
        super(GenerateButton, self).paintEvent(event)

        #setup painter
        qp = QtGui.QPainter(self)
        qp.setRenderHints(qp.Antialiasing)
        qp.setRenderHints(qp.TextAntialiasing)
        qp.setPen(Qt.NoPen)

        #decide palette based on set properties
        if self.property(StyleProperties.DISABLED):
            style = StyleProperties.DISABLED
        elif self.property(StyleProperties.PRESSED):
            style = StyleProperties.PRESSED
        elif self.property(StyleProperties.HOVER):
            style = StyleProperties.HOVER
        else:
            style = ''

        #TODO: should these points/sizes be constants? don't recalculate every time?
        r = self.rect()

        #define corner cutout rects
        corn_tl_pt = QPoint(r.left(), r.top())
        corn_tr_pt = QPoint(r.left() + r.width() - self.BD_SIDE_WIDTH, r.top())
        corn_bl_pt = QPoint(r.left(), r.top() + r.height() - self.BD_TOP_WIDTH)
        corn_br_pt = QPoint(r.left() + r.width() - self.BD_SIDE_WIDTH, r.top() + r.height() - self.BD_TOP_WIDTH)

        corn_rect_size = QSize(self.BD_SIDE_WIDTH, self.BD_TOP_WIDTH)
        corn_tl_rect = QRect(corn_tl_pt, corn_rect_size)
        corn_tr_rect = QRect(corn_tr_pt, corn_rect_size)
        corn_bl_rect = QRect(corn_bl_pt, corn_rect_size)
        corn_br_rect = QRect(corn_br_pt, corn_rect_size)

        #define inner border rects
        bd_left_pt = corn_tl_pt + QPoint(self.BD_OUTER_WIDTH, self.BD_TOP_FULL_WIDTH)
        bd_top_pt = corn_tl_pt + QPoint(self.BD_SIDE_FULL_WIDTH, self.BD_OUTER_WIDTH)
        bd_right_pt = corn_tr_pt + QPoint(-self.BD_OUTER_WIDTH, self.BD_TOP_FULL_WIDTH)
        bd_bottom_pt = corn_bl_pt + QPoint(self.BD_SIDE_FULL_WIDTH, -self.BD_OUTER_WIDTH)

        bd_top_width = r.width() - (2 * self.BD_SIDE_FULL_WIDTH)
        bd_side_height = r.height() - (2 * self.BD_TOP_FULL_WIDTH)

        bd_top_size = QSize(bd_top_width, self.BD_TOP_WIDTH)
        bd_side_size = QSize(self.BD_SIDE_WIDTH, bd_side_height)

        bd_left_rect = QRect(bd_left_pt, bd_side_size)
        bd_top_rect = QRect(bd_top_pt, bd_top_size)
        bd_right_rect = QRect(bd_right_pt, bd_side_size)
        bd_bottom_rect = QRect(bd_bottom_pt, bd_top_size)

        #define central button rect
        btn_tl_pt = r.topLeft() + QPoint(self.BD_SIDE_FULL_WIDTH, self.BD_TOP_FULL_WIDTH)
        btn_tr_pt = r.topRight() + QPoint(-self.BD_SIDE_FULL_WIDTH, self.BD_TOP_FULL_WIDTH)
        btn_bl_pt = r.bottomLeft() + QPoint(self.BD_SIDE_FULL_WIDTH, -self.BD_TOP_FULL_WIDTH)
        btn_br_pt = r.bottomRight() + QPoint(-self.BD_SIDE_FULL_WIDTH, -self.BD_TOP_FULL_WIDTH)

        btn_size = QSize(bd_top_width, bd_side_height)
        btn_rect = QRect(btn_tl_pt, btn_size)

        #draw outer border
        qp.setBrush(QtGui.QBrush(self.getCSSProperty('border-outer-color', style)))
        qp.drawRect(r)

        #"cut out" corners
        qp.setBrush(QtGui.QBrush(self.getCSSProperty('background-color', style)))
        qp.drawRect(corn_tl_rect)
        qp.drawRect(corn_tr_rect)
        qp.drawRect(corn_bl_rect)
        qp.drawRect(corn_br_rect)

        #draw inner borders
        qp.setBrush(QtGui.QBrush(self.getCSSProperty('border-left-color', style)))
        qp.drawRect(bd_left_rect)

        qp.setBrush(QtGui.QBrush(self.getCSSProperty('border-top-color', style)))
        qp.drawRect(bd_top_rect)

        qp.setBrush(QtGui.QBrush(self.getCSSProperty('border-right-color', style)))
        qp.drawRect(bd_right_rect)

        qp.setBrush(QtGui.QBrush(self.getCSSProperty('border-bottom-color', style)))
        qp.drawRect(bd_bottom_rect)

        #draw main button rect
        qp.setBrush(QtGui.QBrush(self.getCSSProperty('button-color', style)))
        qp.drawRect(btn_rect)

    #parse this widget's CSS properties into a dictionary
    def getStyleSheetDict(self):
        ssDict = {}
        ss = self.styleSheet()

        #capture CSS groups with regex
        matches = re.findall(self.REGEX_CAPTURE, ss, flags=re.DOTALL)
        for match in matches:
            #store key-value pairs in dict
            groupDict = {}

            tag = match[0]
            group = match[1]

            #strip extra characters
            if not tag == '':
                tag = re.findall(self.REGEX_CAPTURE_TAG, tag)[0]
                tag = re.sub(self.REGEX_CLEAN_WHITESPACE, '', tag)

            #strip whitespace
            group = re.sub(self.REGEX_CLEAN_WHITESPACE, '', group, flags=re.DOTALL)

            #split group by ';', ignoring empty last element
            for prop in group.split(';')[:-1]:
                #split properties by ':' to get key-value pairs
                p = prop.split(':')

                groupDict[ p[0] ] = p[1]

            #add group dict to full sheet dict
            ssDict[ tag ] = groupDict

        return ssDict

    def getCSSProperty(self, prop, style=''):
        inheritDict = {StyleProperties.DISABLED: '',
                       StyleProperties.PRESSED: StyleProperties.HOVER,
                       StyleProperties.HOVER: '',
                       '': None}

        #end recursion if property could not be found
        if style == None:
            return ''

        #get property from style dictionary
        prop_val = self._styleDict[style].get(prop)

        #if property could not be found, recurse until it is
        if prop_val == None:
            return self.getCSSProperty(prop, inheritDict[style])

        #convert color-type properties into QColor
        if 'rgb(' in prop_val:
            return self.qColorFromRgb(prop_val)

        return prop_val

    #apply setProperty() to this widget and all children
    def setPropertyComplete(self, prop, value):
        self.setProperty(prop, value)
        self._label.setProperty(prop, value)
        self._progress.setProperty(prop, value)

        self.repolish(self)
        self.repolish(self._label)
        self.repolish(self._progress)

    def qColorFromRgb(self, rgb_str):
        #get contents of rgb(...) and remove whitespace
        rgb_tuple = re.findall(self.REGEX_RGB, rgb_str)[0]
        rgb_tuple = re.sub(self.REGEX_CLEAN_WHITESPACE, '', rgb_tuple)

        #split by ',' and create QColor
        rgb = rgb_tuple.split(',')
        rgb = list(map(int, rgb))

        return QtGui.QColor(rgb[0], rgb[1], rgb[2])

    def repolish(self, obj):
        obj.style().unpolish(obj)
        obj.style().polish(obj)
        self._styleDict = self.getStyleSheetDict()



class DeleteButton(QtWidgets.QPushButton):
    def sizeHint(self):
        return QSize(25, 25)

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
            u = QtCore.QFileInfo(u).completeSuffix()

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
        f = QtCore.QFileInfo(file).completeSuffix()

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
            uext = QtCore.QFileInfo(uf).completeSuffix()

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

        self._childFrame.setObjectName('FileButtonFrame')

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

        self.multiDragLeave.emit(self._parent.getIndex(), Constants.MAX_DRAW_MULTI_DRAGDROP)

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
        if(selfIndex >= initIndex + min(Constants.MAX_DRAW_MULTI_DRAGDROP, count)):
            return

        #update styling
        self.setProperty(StyleProperties.DRAG_HELD, True)
        self.setProperty(StyleProperties.ALPHA, Constants.MAX_DRAW_MULTI_DRAGDROP - (selfIndex - initIndex))
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, True)
        self.repolish(self)
        self.repolish(self._childFrame)

    def multiDragLeaveEvent(self, initIndex, count):
        #check if this element should be highlighted
        selfIndex = self._parent.getIndex()
        if(selfIndex < initIndex):
            return
        if(selfIndex >= initIndex + min(Constants.MAX_DRAW_MULTI_DRAGDROP, count)):
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

        self.setProperty(StyleProperties.DRAG_HELD, False)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addStretch(1)
        layout.addWidget(self._img)
        layout.addStretch(1)

        self.setLayout(layout)

        self.setObjectName('NewDiscButton')

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
class DiscListEntry(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(DiscListEntry, self).__init__()

        self._parent = parent

        layout = QtWidgets.QHBoxLayout()

        #child widgets
        self._btnIcon = FileButton(ButtonType.IMAGE, self)
        self._btnTrack = FileButton(ButtonType.TRACK, self)
        self._leTitle = QFocusLineEdit("Track Title", self)
        self._lblIName = QtWidgets.QLabel("internal name", self)
        self._btnDelete = DeleteButton(self)
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

        #container layouts for track title and internal name labels
        self._leTitle.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred))

        ulLayout = QtWidgets.QHBoxLayout()
        ulLayout.addWidget(self._lblIName, 1)
        ulLayout.addWidget(self._btnDelete, 0, Qt.AlignRight)
        ulLayout.setSpacing(0)
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

        #bind other signals
        self._btnDelete.clicked.connect(self.deleteSelf)
        self._btnTrack.fileChanged.connect(self.setTitle)
        self._leTitle.textChanged.connect(self.setSubtitle)

        self.setObjectName('DiscListEntry')
        self._btnIcon.setObjectName('ImageButton')
        self._btnTrack.setObjectName('TrackButton')
        self._leTitle.setObjectName('TitleLineEdit')
        self._lblIName.setObjectName('INameLabel')
        self._btnDelete.setObjectName('DeleteButton')
        self._btnUpArrow.setObjectName('ArrowUp')
        self._btnDownArrow.setObjectName('ArrowDown')

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

    def deleteSelf(self):
        self._parent.removeDiscEntry(self.getIndex())

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
        numname_title = ''.join([ DigitNameDict.get(i, i) for i in title.lower() ])
        internal_name = ''.join([ i for i in numname_title if i.isalpha() ])
        self._lblIName.setText(internal_name)



#blank entry in list of tracks
class NewDiscEntry(QtWidgets.QFrame):
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

        self.setObjectName('NewDiscEntry')

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

        self.icon_multiDrop.connect(self.addExcessEntries)
        self.track_multiDrop.connect(self.addExcessEntries)

        self.setObjectName('DiscList')
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



#overloaded QTabBar, with an animated underline like the Minecraft launcher
class AnimatedTabBar(QtWidgets.QTabBar):

    UL_COLOR = QtGui.QColor(57, 130, 73)
    UL_HEIGHT = 3
    UL_WIDTH_2 = 12

    def __init__(self, parent = None):
        super(AnimatedTabBar, self).__init__(parent)

        self.animations = []
        self._first = True

        self.currentChanged.connect(self.tabChanged)

        self.setObjectName('AnimatedTabBar')

    def paintEvent(self, event):
        super(AnimatedTabBar, self).paintEvent(event)

        selected = self.currentIndex()
        if selected < 0:
            return

        tab = QtWidgets.QStyleOptionTab()
        self.initStyleOption(tab, selected)

        qp = QtGui.QPainter(self)
        qp.setRenderHints(qp.Antialiasing)
        qp.setPen(Qt.NoPen)
        qp.setBrush(QtGui.QBrush(self.UL_COLOR))
        qp.drawRect(self.animations[selected].currentValue())

        style = self.style()
        style.drawControl(style.CE_TabBarTabLabel, tab, qp, self)

    def tabChanged(self, index):
        if self.animations:
            self.animations[index].start()

    def tabInserted(self, index):
        super(AnimatedTabBar, self).tabInserted(index)

        baseRect = self.tabRect(index)

        anim = QtCore.QVariantAnimation()
        anim.setStartValue(self.getUnderlineRect(baseRect, False))
        anim.setEndValue(self.getUnderlineRect(baseRect, True))
        anim.setEasingCurve(QtCore.QEasingCurve.Linear)
        anim.setDuration(125)
        anim.valueChanged.connect(self.update)

        self.animations.insert(index, anim)

        if self._first:
            self._first = False
            anim.start()

    def tabRemoved(self, index):
        super(AnimatedTabBar, self).tabRemoved(index)

        anim = self.animations.pop(index)
        anim.stop()
        anim.deleteLater()

    #calculate underline QRect coordinates from tab QRect coordinates
    def getUnderlineRect(self, tabRect, hasWidth=True):
        ulRect = tabRect
        ulRect.setTop(tabRect.bottom() - self.UL_HEIGHT)

        center = tabRect.center().x()

        if hasWidth:
            ulRect.setLeft(center - self.UL_WIDTH_2)
            ulRect.setRight(center + self.UL_WIDTH_2)
        else:
            ulRect.setLeft(center)
            ulRect.setRight(center)

        return ulRect



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



class SettingsListEntry(QtWidgets.QFrame):
    def __init__(self, key, label, settingType = SettingType.PACKPNG, params = None, parent = None):
        super(SettingsListEntry, self).__init__(parent)

        self._parent = parent
        self._key = key

        self._label = QtWidgets.QLabel(label)
        self._selector = SettingsSelector(settingType, params, self)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(5, 5, 5, 5)

        if not settingType == SettingType.PACKPNG:
            layout.setContentsMargins(50, -1, -1, -1)

        layout.addWidget(self._selector.getWidget())
        layout.addWidget(self._label)
        layout.addStretch(1)

        self.setLayout(layout)

        self._label.setObjectName('SettingLabel')

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

        self._childLayout.addWidget(SettingsListEntry('pack', "Pack icon (optional)", SettingType.PACKPNG))
        #self._childLayout.addWidget(SettingsListEntry('version', "Game version", SettingType.DROPDOWN, ['1.17', '1.16']))
        self._childLayout.addWidget(SettingsListEntry('zip', "Generate pack as .zip", SettingType.CHECK))
        #self._childLayout.addWidget(SettingsListEntry('mix_mono', "Mix stereo tracks to mono", SettingType.CHECK))
        #self._childLayout.addWidget(SettingsListEntry('keep_tmp', "Keep intermediate converted files", SettingType.CHECK))
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

        self.setObjectName('SettingsList')
        widget.setObjectName('SettingsChildWidget')
        scrollArea.setObjectName('SettingsScrollArea')

    def getUserSettings(self):
        settingsDict = {}
        for i in range(self._childLayout.count()):
            e = self._childLayout.itemAt(i).widget()

            if(type(e) == SettingsListEntry):
                settingsDict.update(e.getKeyValue())

        return settingsDict



#semi-transparent popup to display errors during pack generation
class StatusDisplayWidget(QtWidgets.QLabel):
    def __init__(self, text, relativeWidget, parent = None):
        super(StatusDisplayWidget, self).__init__(text, parent)

        self._parent = parent
        self._widget = relativeWidget
        self._basePos = QPoint(0,0)

        self.setProperty(StyleProperties.ERROR, False)
        #self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAutoFillBackground(True)
        self.setVisible(False)

        #slide in/out animation
        self.animation = QtCore.QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)

        #automatic hide timer
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(Constants.STATUS_MESSAGE_SHOW_TIME_MS)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

        self.setObjectName('StatusDisplay')

    def mousePressEvent(self, event):
        event.accept()
        self.hide()

    def repolish(self, obj):
        obj.style().unpolish(obj)
        obj.style().polish(obj)

    #widget is not part of a layout, so position has to be updated manually
    def setBasePos(self):
        r = self.rect()
        w_pos = self._widget.mapToParent( QPoint(0,0) )
        w_pos = w_pos - QPoint(0, r.height())

        self._basePos = w_pos

        if self.isVisible():
            self.setGeometry(w_pos.x(), w_pos.y(), r.width(), r.height())

    def unsetVisible(self):
        self.animation.finished.disconnect()
        self.setVisible(False)

    def show(self, status):
        #use status to decide text and bg color
        self.setText(StatusMessageDict.get(status, 'Unknown error.'))
        self.adjustSize()

        self.setProperty(StyleProperties.ERROR, (status != Status.SUCCESS) )
        self.repolish(self)

        #set start and end points
        r = self.rect()
        startRect = QRect(self._basePos - QPoint(r.width(),0), r.size())
        endRect = QRect(self._basePos, r.size())

        #start animation and auto-hide timer
        self.animation.stop()
        self.animation.setStartValue(startRect)
        self.animation.setEndValue(endRect)
        self.animation.start()
        self.timer.start()

        self.setVisible(True)

    def hide(self):
        #set start and end points
        r = self.rect()
        startRect = QRect(self._basePos, r.size())
        endRect = QRect(self._basePos - QPoint(r.width(),0), r.size())

        #start animation
        self.timer.stop()
        self.animation.stop()
        self.animation.finished.connect(self.unsetVisible)
        self.animation.setStartValue(startRect)
        self.animation.setEndValue(endRect)
        self.animation.start()



#primary container widget
class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(CentralWidget, self).__init__(parent)

        self._parent = parent

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
        tabs = QtWidgets.QTabWidget(self)
        tabs.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        tabs.setStyleSheet(CSS_STYLESHEET)

        #set tabs background color
        tabs.setAutoFillBackground(True)
        palette = tabs.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(32, 32, 32))
        tabs.setPalette(palette)

        tabBar = AnimatedTabBar(self)
        tabs.setTabBar(tabBar)
        tabs.addTab(self._discList, "    Tracks    ")
        tabs.addTab(self._settingsList, "    Settings    ")
        layout.addWidget(tabs, 0)

        #button to generate datapack/resourcepack
        self._btnGen = GenerateButton(self)
        self._btnGen.generate.connect(self.generatePacks)

        #wrap inside container frame and layout, for aesthetics
        btnLayout = QtWidgets.QHBoxLayout(self)
        btnLayout.setSpacing(0)
        btnLayout.setContentsMargins(0, 5, 0, 5)
        btnLayout.addStretch()
        btnLayout.addWidget(self._btnGen, 0, Qt.AlignBottom)
        btnLayout.addStretch()

        btnFrame = QtWidgets.QFrame(self)
        btnFrame.setLayout(btnLayout)
        layout.addWidget(btnFrame)
        self.setLayout(layout)

        self.setObjectName('CentralWidget')
        tabs.setObjectName('AnimatedTabs')
        btnFrame.setObjectName('GenFrame')

        self.setStyleSheet(CSS_STYLESHEET)

        #status display bar
        self._status = StatusDisplayWidget('', btnFrame, self)
        self._parent.resized.connect(self._status.setBasePos)

        #arrange draw order
        btnFrame.raise_()
        self._status.raise_()

    def showEvent(self, event):
        super(CentralWidget, self).showEvent(event)

        #setup status display bar, now that widget coordinates are determined
        self._status.adjustSize()
        self._status.setBasePos()

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
        self._thread = QtCore.QThread(self)
        self._worker = GeneratePackWorker(settings, texture_files, track_files, titles, internal_names)
        self._worker.moveToThread(self._thread)

        self._worker.started.connect(lambda: self._btnGen.setCurrentIndex.emit(1))
        self._worker.finished.connect(lambda: self._btnGen.setCurrentIndex.emit(0))
        self._worker.status.connect(self._status.show)

        self._worker.min_prog.connect(self._btnGen._progress.setMinimum)
        self._worker.progress.connect(self._btnGen._progress.setValue)
        self._worker.max_prog.connect(self._btnGen._progress.setMaximum)

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
class GeneratePackWorker(QtCore.QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    status = pyqtSignal(Status)
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
        self.started.emit()

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
        if not status == Status.SUCCESS:
            self.status.emit(status)
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
            if not status == Status.SUCCESS:
                self.status.emit(status)
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
        if not status == Status.SUCCESS:
            self.status.emit(status)

            if not status == Status.BAD_ZIP:
                self.finished.emit()
                return

        progress += 1
        self.progress.emit(progress)

        status = generator.generate_resourcepack(self._texture_files,
                                                 self._track_files,
                                                 self._titles,
                                                 self._internal_names,
                                                 self._settings)
        if not status == Status.SUCCESS:
            self.status.emit(status)

            if not status == Status.BAD_ZIP:
                self.finished.emit()
                return

        progress += 1
        self.progress.emit(progress)

        print("Successfully generated datapack and resourcepack!")

        self.status.emit(status)
        self.finished.emit()


