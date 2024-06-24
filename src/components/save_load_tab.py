from PySide6 import QtWidgets


class SaveLoadTab(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self.setObjectName(type(self).__name__)
        self._parent = parent

        self.layout = QtWidgets.QVBoxLayout(self)
        self.save_button = QtWidgets.QPushButton("Save")
        self.load_button = QtWidgets.QPushButton("Load")
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.load_button)
