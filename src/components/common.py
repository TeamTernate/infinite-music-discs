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

from src.definitions import Assets, Constants, ButtonType, Helpers, Status, FileExt, StyleProperties
from src.definitions import StatusMessageDict, StatusStickyDict, GB_CSS_STYLESHEET



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

        #if so, highlight with gradient
        self.highlightStyling(initIndex, selfIndex)

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

        #remove highlight since files were dropped
        self.resetStyling()

        return (selfIndex - initIndex)

    def highlightStyling(self, initIndex, selfIndex):
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
    def multiDropEvent(self, initIndex, files):
        #TODO: maybe bad practice to have super return value but child doesn't?
        #   maybe better to have helper function defined elsewhere that parent uses

        #TODO: actually pass an event into these functions?
        #  check if event.isAccepted instead of returning value
        dropIndex = super().multiDropEvent(initIndex, files)
        if dropIndex < 0:
            return

        #set text from line in file
        self.setText(files[dropIndex])

    def highlightStyling(self, initIndex, selfIndex):
        self.setProperty(StyleProperties.DRAG_HELD, True)
        self.setProperty(StyleProperties.ALPHA, Constants.MAX_DRAW_MULTI_DRAGDROP - (selfIndex - initIndex))
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



#button for generating datapack/resourcepack
#TODO: optimize a lot
#TODO: don't use properties? what's the point if you're just overriding them with stylesheets anyway
#TODO: use something other than stylesheet for optimization? or are there built in methods to parse stylesheet?
class GenerateButton(QRepolishMixin, QtWidgets.QPushButton, QSetsNameFromType):

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
        super().__init__(parent=parent)

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
        lytLabel.setContentsMargins(0, 0, 0, 0)
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

        self._label.setObjectName('GenLabel')
        self._progress.setObjectName('GenProgress')

        self._styleSheet = GB_CSS_STYLESHEET
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
        super().paintEvent(event)

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
        ss = self._styleSheet

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
        if style is None:
            return ''

        #get property from style dictionary
        prop_val = self._styleDict[style].get(prop)

        #if property could not be found, recurse until it is
        if prop_val is None:
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
        self._styleDict = self.getStyleSheetDict()

    def qColorFromRgb(self, rgb_str):
        #get contents of rgb(...) and remove whitespace
        rgb_tuple = re.findall(self.REGEX_RGB, rgb_str)[0]
        rgb_tuple = re.sub(self.REGEX_CLEAN_WHITESPACE, '', rgb_tuple)

        #split by ',' and create QColor
        rgb = rgb_tuple.split(',')
        rgb = list(map(int, rgb))

        return QtGui.QColor(rgb[0], rgb[1], rgb[2])



#file selection button supporting file drag/drop
class DragDropButton(QDragDropMixin, QRepolishMixin, QtWidgets.QPushButton, QSetsNameFromType):

    fileChanged = pyqtSignal(list)

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
        self._img = QtWidgets.QLabel()
        self._img.setScaledContents(True)
        self.setImage(self._file)

    def sizeHint(self):
        return(QSize(80, 80))

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

        #TODO: move this somewhere more global ^ top of class maybe
        assetDict = {
            FileExt.PNG: self._file,
            FileExt.OGG: Assets.ICON_OGG,
            FileExt.MP3: Assets.ICON_MP3,
            FileExt.WAV: Assets.ICON_WAV
        }

        #TODO: use another dictionary to nest this decision logic
        imgPath = ''
        if(self._type == ButtonType.IMAGE):
            imgPath = assetDict.get(f, Assets.ICON_ICON_EMPTY)
        elif(self._type == ButtonType.TRACK):
            imgPath = assetDict.get(f, Assets.ICON_TRACK_EMPTY)
        elif(self._type == ButtonType.PACKPNG):
            imgPath = assetDict.get(f, Assets.ICON_PACK_EMPTY)
        elif(self._type == ButtonType.NEW_TRACK):
            self.setText('+')
            #imgPath = Assets.ICON_NEW_DISC
        else:
            pass

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
        if(self._type == ButtonType.IMAGE):
            return ( ext in [ FileExt.PNG ] )
        if(self._type == ButtonType.PACKPNG):
            return ( ext in [ FileExt.PNG ] )
        if(self._type == ButtonType.TRACK):
            return ( ext in [ FileExt.MP3, FileExt.WAV, FileExt.OGG ] )
        if(self._type == ButtonType.NEW_TRACK):
            return ( ext in [ FileExt.MP3, FileExt.WAV, FileExt.OGG ] )



#child of DragDropButton supporting multi-file drag-drop
class FileButton(QMultiDragDropMixin, DragDropButton):
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

        self._childFrame.setObjectName('FileButtonFrame')

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

    def multiDropEvent(self, initIndex, files):
        dropIndex = super().multiDropEvent(initIndex, files)
        if dropIndex < 0:
            return

        #save file
        self.setFile(files[dropIndex])
        self.fileChanged.emit([ files[dropIndex] ])

    def highlightStyling(self, initIndex, selfIndex):
        self.setProperty(StyleProperties.DRAG_HELD, True)
        self.setProperty(StyleProperties.ALPHA, Constants.MAX_DRAW_MULTI_DRAGDROP - (selfIndex - initIndex))
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, True)
        self.repolish(self)
        self.repolish(self._childFrame)

    def resetStyling(self):
        self.setProperty(StyleProperties.DRAG_HELD, False)
        self.setProperty(StyleProperties.ALPHA, 10)
        self._childFrame.setProperty(StyleProperties.DRAG_HELD, False)
        self.repolish(self)
        self.repolish(self._childFrame)



#overloaded QTabBar, with an animated underline like the Minecraft launcher
class AnimatedTabBar(QtWidgets.QTabBar, QSetsNameFromType):

    UL_COLOR = QtGui.QColor(57, 130, 73)
    UL_HEIGHT = 3
    UL_WIDTH_2 = 12

    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self.animations = []
        self._first = True

        self.currentChanged.connect(self.tabChanged)

    def paintEvent(self, event):
        super().paintEvent(event)

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
        #clear focused widget from previous tab
        focusWidget = QtWidgets.QApplication.focusWidget()

        if focusWidget is not None:
            focusWidget.clearFocus()

        #start transition animation
        if self.animations:
            self.animations[index].start()

    def tabInserted(self, index):
        super().tabInserted(index)

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
        super().tabRemoved(index)

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



#semi-transparent popup to display errors during pack generation
class StatusDisplayWidget(QRepolishMixin, QtWidgets.QLabel, QSetsNameFromType):
    def __init__(self, text, relativeWidget, parent = None):
        super().__init__(text=text, parent=parent)

        self._parent = parent
        self._widget = relativeWidget
        self._basePos = QPoint(0,0)

        self.sticky = False

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

    def mousePressEvent(self, event):
        event.accept()
        self.hide()

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

        #errors during generation are marked 'sticky' so the user doesn't miss them
        self.sticky = StatusStickyDict.get(status, False)

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

        if not self.sticky:
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


