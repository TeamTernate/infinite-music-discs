#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack GUI execution module
#Generation tool, datapack design, and resourcepack design by link2_thepast

#TODO: offer legacy datapack in 1.21+ ? some NBT paths in the jukebox block changed, may not be worth maintaining
#TODO: consider indicating which version of the datapack/resourcepack you're going to get when you generate

#TODO: tint DiscListEntries during pack generation, display pass/fail indicators showing which ones finished
#  successfully and which ones caused an error (if any)
#TODO: display "converting track x/y" to indicate progress? necessary?

#TODO: can you generate disc textures automatically using armor trims?

#TODO: default mix_mono to on?

#TODO: test pack with 1000+ files, make sure nothing breaks

#TODO: try out supported_formats for future versions

import sys
import ctypes
import platform
import logging
import multiprocessing

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from src.definitions import Assets, Constants
from src.components.top import CentralWidget



class UI(QtWidgets.QMainWindow):
    resized = QtCore.Signal()
    moved = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle(Constants.APP_TITLE)
        self.setWindowIcon(QtGui.QIcon(Assets.APP_ICON))
        self.setCentralWidget( CentralWidget(self) )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.moved.emit()



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

    if issubclass(cls, KeyboardInterrupt):
        return

    logger.critical(Constants.LOG_EXC_MSG, exc_info=(cls, exception, traceback))



if __name__ == "__main__":
    # allow multiprocessing to work when compiled for Windows
    # doesn't do anything on Mac or Linux
    multiprocessing.freeze_support()

    # log exceptions to console and a logfile
    logger = logging.getLogger(__name__)
    logger.addHandler( logging.FileHandler(Constants.LOG_FILE_NAME, delay=True) )
    sys.excepthook = except_hook

    #platform-specific behaviors
    sys_os = platform.system()
    if sys_os == 'Windows':
        app_id = 'teamternate.imd.imd_gui.01'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    elif sys_os == 'Darwin':
        #macOS behavior here
        pass

    elif sys_os == 'Linux':
        #linux behavior here
        pass

    #init app and begin
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    #app was not designed for high DPI, round to integer
    #  scale factor; 1.0 if possible
    #TODO: redesign ui for high DPI?
    app.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.Floor)

    ui = UI()
    ui.resize(500, 650)
    ui.setMinimumSize(400, 500)
    ui.show()

    sys.exit(app.exec())
