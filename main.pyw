#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack GUI execution module
#Generation tool, datapack design, and resourcepack design by link2_thepast

import sys
import ctypes
import platform

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from src.components import CentralWidget

class UI(QtWidgets.QMainWindow):
    resized = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IMD Datapack Generator")
        self.setWindowIcon(QtGui.QIcon('data/jukebox_256.png'))

        self._centralWidget = CentralWidget(self)
        self.setCentralWidget(self._centralWidget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)



if __name__ == "__main__":
    sys.excepthook = except_hook

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

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    
    ui = UI()
    ui.resize(500, 650)
    ui.setMinimumSize(400, 500)
    ui.show()

    sys.exit(app.exec_())
