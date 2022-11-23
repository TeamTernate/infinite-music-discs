#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack GUI components module
#Generation tool, datapack design, and resourcepack design by link2_thepast

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal

from src import generator
from src.definitions import Status
from src.definitions import CSS_STYLESHEET

from src.components.common import QSetsNameFromType, AnimatedTabBar, GenerateButton, StatusDisplayWidget
from src.components.settings_tab import SettingsList
from src.components.tracks_tab import DiscList



#TODO: move primary widget into its own separate file
#   separate files for DiscList and SettingsList
#   generally, separate files for different tabs
#TODO: standardize where size policies are set - probably inside widget's own init makes more sense
#primary container widget
class CentralWidget(QtWidgets.QWidget, QSetsNameFromType):
    windowMoved = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent=parent)

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

    def showEvent(self, event):
        super().showEvent(event)

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

        #TODO: try to use 1 dictionary instead of parallel lists
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
    started = pyqtSignal()
    finished = pyqtSignal()
    valid = pyqtSignal()
    status = pyqtSignal(Status)
    min_prog = pyqtSignal(int)
    progress = pyqtSignal(int)
    max_prog = pyqtSignal(int)

    def __init__(self, settings, texture_files, track_files, titles, internal_names):
        super().__init__()

        self._settings = settings
        self._texture_files = texture_files
        self._track_files = track_files
        self._titles = titles
        self._internal_names = internal_names

    #TODO: make the status returning system more elegant - function to capture status and check that it's not success?
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
        self.valid.emit()

        for i in range(len(self._track_files)):
            #wrap string in list to allow C-style passing by reference
            wrapper = [ self._track_files[i] ]
            status = generator.convert_to_ogg(wrapper,
                                              self._internal_names[i],
                                              self._settings['mix_mono'],
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


