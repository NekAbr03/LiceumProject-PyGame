import sys

from PyQt5 import uic
from PyQt5.QtWidgets import *
from megagamedesign import Ui_MainWindow


class GameStartWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.setGeometry(200, 100, 1000, 650)
        self.setWindowTitle('Mario')
        self.pushButton.setObjectName("button_play")
        self.pushButton_2.setObjectName("button_rez")
        self.label.setObjectName("label_main")
        self.pushButton_3.setObjectName("button_exit")
        self.label_2.setObjectName("label_rez")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2.setObjectName("pushButton_2")
        self.label.setObjectName("label")
        self.pushButton_3.setObjectName("pushButton_3")
        self.label_2.setObjectName("label_2")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = GameStartWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
