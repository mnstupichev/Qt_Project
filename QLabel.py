from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel


class QLabelAlterada(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

    clicked = pyqtSignal()
    rightClicked = pyqtSignal()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            self.clicked.emit()
