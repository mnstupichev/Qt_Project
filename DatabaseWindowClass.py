from PyQt5.QtWidgets import QMainWindow,  QTableWidgetItem
from Database import Ui_MainWindow1

class DatabaseWindow(QMainWindow, Ui_MainWindow1):
    def __init__(self, db):
        super().__init__()
        self.setupUi(self)
        self.db = db
        self.cur = self.db.conn.cursor()
        self.result = self.cur.execute("""SELECT * FROM actions""").fetchall()
        self.tableWidget.setRowCount(len(self.result))
        self.style_sheet()
        self.make_database()


    def style_sheet(self):
        self.setStyleSheet("background-color: rgb(61, 43, 33);")
        self.tableWidget.setStyleSheet("background-color: rgb(155, 120, 80)")

    def make_database(self):
        for i, elem in enumerate(self.result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
                self.tableWidget.resizeColumnsToContents()
