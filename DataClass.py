import sqlite3

class Data:
    def __init__(self):
        self.conn = sqlite3.connect('actions.db')
