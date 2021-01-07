import sys

from PyQt5.QtWidgets import *

from megagamedesign import Ui_MainWindow


class GameStartWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 100, 1000, 650)
        self.setWindowTitle('Mario')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = GameStartWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
