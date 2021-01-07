import sys
from PyQt5.QtWidgets import *
from megagamedesign import Ui_MainWindow


class GameStartWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
