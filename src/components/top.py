# -*- coding: utf-8 -*-
#
#Infinite Music Discs top-level GUI components module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from typing import Any

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal, QSize, QPoint, QRect

import src.generator.factory as generator_factory
from src.definitions import Status, IMDException, DiscListContents
from src.definitions import CSS_STYLESHEET

from src.definitions import Assets, Constants, StyleProperties, StatusMessageDict, StatusStickyDict, GenerateButtonColorsDict
from src.components.common import QRepolishMixin
from src.components.settings_tab import SettingsList
from src.components.tracks_tab import DiscList



#button for generating datapack/resourcepack
class GenerateButton(QRepolishMixin, QtWidgets.QPushButton):

    BD_OUTER_WIDTH = 2
    BD_TOP_WIDTH = 4
    BD_SIDE_WIDTH = 5

    BD_TOP_FULL_WIDTH = BD_OUTER_WIDTH + BD_TOP_WIDTH
    BD_SIDE_FULL_WIDTH = BD_OUTER_WIDTH + BD_SIDE_WIDTH

    generate = Signal()
    setCurrentIndex = Signal(int)

    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self.setObjectName(type(self).__name__)
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
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
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

    def sizeHint(self) -> QSize:
        return QSize(350, 66)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        event.accept()
        self.setPropertyComplete(StyleProperties.PRESSED, True)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        event.accept()
        self.setPropertyComplete(StyleProperties.PRESSED, False)
        self.generate.emit()

    def enterEvent(self, event: QtGui.QEnterEvent):
        event.accept()
        self.setPropertyComplete(StyleProperties.HOVER, True)

    def leaveEvent(self, event: QtCore.QEvent):
        event.accept()
        self.setPropertyComplete(StyleProperties.PRESSED, False)
        self.setPropertyComplete(StyleProperties.HOVER, False)

    def changeEvent(self, event: QtCore.QEvent):
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

    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)

        #setup painter
        qp = QtGui.QPainter(self)
        qp.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing)
        qp.setRenderHints(QtGui.QPainter.RenderHint.TextAntialiasing)
        qp.setPen(Qt.NoPen)

        #decide palette based on set properties
        # disabled > pressed > hover > base colors
        if self.property(StyleProperties.DISABLED):
            style = StyleProperties.DISABLED
        elif self.property(StyleProperties.PRESSED):
            style = StyleProperties.PRESSED
        elif self.property(StyleProperties.HOVER):
            style = StyleProperties.HOVER
        else:
            style = StyleProperties.BASE

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
        btn_size = QSize(bd_top_width, bd_side_height)
        btn_rect = QRect(btn_tl_pt, btn_size)

        #draw outer border
        qp.setBrush(QtGui.QBrush(GenerateButtonColorsDict['border-outer-color'][style]))
        qp.drawRect(r)

        #"cut out" corners
        qp.setBrush(QtGui.QBrush(GenerateButtonColorsDict['background-color'][style]))
        qp.drawRect(corn_tl_rect)
        qp.drawRect(corn_tr_rect)
        qp.drawRect(corn_bl_rect)
        qp.drawRect(corn_br_rect)

        #draw inner borders
        qp.setBrush(QtGui.QBrush(GenerateButtonColorsDict['border-left-color'][style]))
        qp.drawRect(bd_left_rect)

        qp.setBrush(QtGui.QBrush(GenerateButtonColorsDict['border-top-color'][style]))
        qp.drawRect(bd_top_rect)

        qp.setBrush(QtGui.QBrush(GenerateButtonColorsDict['border-right-color'][style]))
        qp.drawRect(bd_right_rect)

        qp.setBrush(QtGui.QBrush(GenerateButtonColorsDict['border-bottom-color'][style]))
        qp.drawRect(bd_bottom_rect)

        #draw main button rect
        qp.setBrush(QtGui.QBrush(GenerateButtonColorsDict['button-color'][style]))
        qp.drawRect(btn_rect)

    #apply setProperty() to this widget and all children
    #properties are used to select different CSS styles
    def setPropertyComplete(self, prop: StyleProperties, value: Any):
        self.setProperty(prop, value)
        self._label.setProperty(prop, value)
        self._progress.setProperty(prop, value)

        self.repolish(self)
        self.repolish(self._label)
        self.repolish(self._progress)



#overloaded QTabBar, with an animated underline like the Minecraft launcher
class AnimatedTabBar(QtWidgets.QTabBar):

    UL_COLOR = QtGui.QColor(57, 130, 73)
    UL_HEIGHT = 3
    UL_WIDTH_2 = 12

    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self.setObjectName(type(self).__name__)

        self.animations = []
        self._first = True

        self.currentChanged.connect(self.tabChanged)

    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)

        selected = self.currentIndex()
        if selected < 0:
            return

        tab = QtWidgets.QStyleOptionTab()
        self.initStyleOption(tab, selected)

        qp = QtGui.QPainter(self)
        qp.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing)
        qp.setPen(Qt.NoPen)
        qp.setBrush(QtGui.QBrush(self.UL_COLOR))
        qp.drawRect(self.animations[selected].currentValue())

        style = self.style()
        style.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, tab, qp, self)

    def tabChanged(self, index: int):
        #clear focused widget from previous tab
        focusWidget = QtWidgets.QApplication.focusWidget()

        if focusWidget is not None:
            focusWidget.clearFocus()

        #start transition animation
        if self.animations:
            self.animations[index].start()

    def tabInserted(self, index: int):
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

    def tabRemoved(self, index: int):
        super().tabRemoved(index)

        anim = self.animations.pop(index)
        anim.stop()
        anim.deleteLater()

    #calculate underline QRect coordinates from tab QRect coordinates
    def getUnderlineRect(self, tabRect: QRect, hasWidth=True) -> QRect:
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
class StatusDisplayWidget(QRepolishMixin, QtWidgets.QLabel):
    def __init__(self, text: str, relativeWidget: QtWidgets.QWidget, parent = None):
        super().__init__(text=text, parent=parent)

        self.setObjectName(type(self).__name__)
        self._parent = parent

        self._widget = relativeWidget

        self._basePos = QPoint(0,0)
        self._showRect = self.rect()
        self._hideRect = self.rect()

        self.sticky = False

        self.setProperty(StyleProperties.ERROR, False)
        #self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAutoFillBackground(True)
        self.setVisible(False)

        #slide in/out animations
        self.showAnimation = QtCore.QPropertyAnimation(self, b"geometry")
        self.showAnimation.setDuration(Constants.STATUS_MESSAGE_ANIM_TIME_MS)
        self.showAnimation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        self.showAnimation.setStartValue(self._hideRect)
        self.showAnimation.setEndValue(self._showRect)

        self.hideAnimation = QtCore.QPropertyAnimation(self, b"geometry")
        self.hideAnimation.setDuration(Constants.STATUS_MESSAGE_ANIM_TIME_MS)
        self.hideAnimation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        self.hideAnimation.setStartValue(self._showRect)
        self.hideAnimation.setEndValue(self._hideRect)
        self.hideAnimation.finished.connect(self.unsetVisible)

        #automatic hide timer
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(Constants.STATUS_MESSAGE_SHOW_TIME_MS)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        event.accept()
        self.hide()

    #widget is not part of a layout, so position has to be updated manually
    #set animation start/end pos after widget gets its proper position
    def setBasePos(self):
        r = self.rect()
        w_pos = self._widget.mapToParent( QPoint(0,0) )
        w_pos = w_pos - QPoint(0, r.height())

        self._basePos = w_pos

        if self.isVisible():
            self.setGeometry(w_pos.x(), w_pos.y(), r.width(), r.height())

    def unsetVisible(self):
        self.setVisible(False)

    def show(self, status: Status):
        #use status to decide text and bg color
        #resize widget to fit text
        self.setText(StatusMessageDict.get(status, 'Unknown error.'))
        self.adjustSize()

        #errors during generation are marked 'sticky' so the user doesn't miss them
        self.sticky = StatusStickyDict.get(status, False)

        self.setProperty(StyleProperties.ERROR, (status != Status.SUCCESS) )
        self.repolish(self)

        #update start and end points now that widget has resized
        r = self.rect()
        self._showRect = QRect(self._basePos, r.size())
        self._hideRect = QRect(self._basePos - QPoint(r.width(),0), r.size())

        self.showAnimation.setStartValue(self._hideRect)
        self.showAnimation.setEndValue(self._showRect)

        self.hideAnimation.setStartValue(self._showRect)
        self.hideAnimation.setEndValue(self._hideRect)

        #start animation and the auto-hide timer
        self.showAnimation.stop()
        self.hideAnimation.stop()
        self.showAnimation.start()

        if not self.sticky:
            self.timer.start()

        self.setVisible(True)

    def hide(self):
        #start animation and stop the auto-hide timer
        #widget is hiding, no need to trigger hide again
        self.timer.stop()
        self.showAnimation.stop()
        self.hideAnimation.stop()
        self.hideAnimation.start()



#TODO: standardize where size policies are set - probably inside widget's own init makes more sense
#primary container widget
class CentralWidget(QtWidgets.QWidget):
    windowMoved = QtCore.Signal()

    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self.setObjectName(type(self).__name__)
        self._parent = parent

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        #list of music disc tracks
        self._discList = DiscList(self)
        self._discList.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)

        #generation settings
        self._settingsList = SettingsList(self)
        self._settingsList.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)

        #tabs to switch between track list and settings
        tabs = QtWidgets.QTabWidget(self)
        tabs.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)

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

        tabs.setObjectName('AnimatedTabs')
        btnFrame.setObjectName('GenFrame')

        self.setStyleSheet(CSS_STYLESHEET)

        #provide children with a "window moved" signal
        #  widgets never move relative to their containing window, and cannot detect window movement on their own
        self._parent.moved.connect(self.windowMoved)

        #status display bar
        self._status = StatusDisplayWidget('', btnFrame, self)
        self._parent.resized.connect(self._status.setBasePos)

        #arrange draw order
        btnFrame.raise_()
        self._status.raise_()

    def showEvent(self, event: QtGui.QShowEvent):
        super().showEvent(event)

        #setup status display bar, now that widget coordinates are determined
        self._status.adjustSize()
        self._status.setBasePos()

    def generatePacks(self):
        entry_list = self._discList.getDiscEntries()
        settings = self._settingsList.getUserSettings()

        #launch worker thread to generate packs
        #   FFmpeg conversion is slow, don't want to lock up UI
        self._thread = QtCore.QThread(self)
        self._worker = GeneratePackWorker(entry_list, settings)
        self._worker.moveToThread(self._thread)

        self._worker.started.connect(lambda: self._btnGen.setCurrentIndex.emit(1))
        self._worker.finished.connect(lambda: self._btnGen.setCurrentIndex.emit(0))
        self._worker.status.connect(self._status.show)
        self._worker.valid.connect(self._status.hide)

        self._worker.min_prog.connect(self._btnGen._progress.setMinimum)
        self._worker.progress.connect(self._btnGen._progress.setValue)
        self._worker.max_prog.connect(self._btnGen._progress.setMaximum)

        self._thread.started.connect(self._worker.generate)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.destroyed.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._btnGen.setEnabled(False)
        self._thread.finished.connect(lambda: self._btnGen.setEnabled(True))

        self._thread.start()



#worker object that generates the datapack/resourcepack in a separate QThread
class GeneratePackWorker(QtCore.QObject):
    started = Signal()
    finished = Signal()
    valid = Signal()
    status = Signal(Status)
    min_prog = Signal(int)
    progress = Signal(int)
    max_prog = Signal(int)

    def __init__(self, entry_list: DiscListContents, settings: dict):
        super().__init__()

        self._generator = generator_factory.get(settings)

        self._entry_list = entry_list
        self._settings = settings
        self._progress = 0

    def emit_update_progress(self):
        self._progress += 1
        self.progress.emit(self._progress)

    # multiprocessing's apply_async needs a callback
    #   that accepts 1 argument, even if you don't do
    #   anything with it
    def convert_cb(self, x):
        self.emit_update_progress()

    def generate(self):
        try:
            self.run()

        except IMDException as e:
            self.status.emit(e.status)
        else:
            self.status.emit(Status.SUCCESS)

        finally:
            self.finished.emit()

    def run(self):
        self.started.emit()

        #total steps = validate + num track conversions + generate dp + generate rp
        self.min_prog.emit(0)
        self.progress.emit(0)
        self.max_prog.emit(1 + len(self._entry_list) + 1 + 1)

        self._progress = 0

        #make sure data is valid before continuing
        self._generator.validate(self._entry_list, self._settings)
        self.emit_update_progress()
        self.valid.emit()

        #process tracks
        self._generator.create_tmp()
        self._generator.convert_all_to_ogg(self._entry_list, self._settings, self.emit_update_progress)

        #post-process tracks individually       
        for e in self._entry_list.entries:
            # e.track_file = self._generator.convert_to_ogg(e, self._settings)
            e.length_s = self._generator.get_track_length(e)
            e.length_t = self._generator.seconds_to_ticks(e.length_s)
            e.title = self._generator.sanitize(e)
            self.emit_update_progress()

        #generate datapack
        self._generator.generate_datapack(self._entry_list, self._settings)
        self.emit_update_progress()

        #generate resourcepack
        self._generator.generate_resourcepack(self._entry_list, self._settings)
        self.emit_update_progress()

        #finish up and return to generate()
        self._generator.cleanup_tmp()
        print("Successfully generated datapack and resourcepack!")


