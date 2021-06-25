#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Infinite Music Discs datapack + resourcepack GUI execution module
#Generation tool, datapack design, and resourcepack design by link2_thepast

import sys
from PyQt5 import QtWidgets

from components import CentralWidget

class UI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IMD Datapack Generator")

        self._centralWidget = CentralWidget(self)
        self.setCentralWidget(self._centralWidget)



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)



if __name__ == "__main__":
    sys.excepthook = except_hook
    
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    
    ui = UI()
    ui.resize(500, 650)
    ui.setMinimumSize(400, 500)
    ui.show()

    sys.exit(app.exec_())
