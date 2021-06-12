import sys
from PyQt5 import QtWidgets

from components import CentralWidget

class UI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IMD Datapack Generator")

        self._centralWidget = CentralWidget(self)
        self.setCentralWidget(self._centralWidget)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    
    ui = UI()
    ui.resize(400, 500)
    ui.setMinimumSize(400, 500)
    ui.show()
    sys.exit(app.exec_())
