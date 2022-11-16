from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel


class QPushButton_with_image(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

    clicked = pyqtSignal()
    right_clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.right_clicked.emit()
        else:
            self.clicked.emit()
