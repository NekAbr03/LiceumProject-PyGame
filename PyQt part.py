import sys
import sqlite3
from PyQt5.QtGui import QFont, QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import *

from megagamedesign import Ui_MainWindow


class GameStartWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.button_exit.clicked.connect(self.close_window)
        self.button_rez.clicked.connect(self.open_result)

    def close_window(self):
        self.close()

    def open_result(self):  # окно с таблицей результатов
        self.window_res = Results()
        self.window_res.show()

    def update_res(self):  # обновление результата в label_rez
        pass


class Results(QWidget):
    def __init__(self):
        super().__init__()
        self.font = QFont()

        self.setGeometry(1460, 185, 500, 500)
        self.setWindowTitle("Результаты")

        self.button_close_res = QPushButton(self)
        self.button_close_res.resize(150, 50)
        self.button_close_res.move(350, 430)
        self.button_close_res.setText('Закрыть')

        self.label_res = QLabel(self)
        self.label_res.resize(500, 450)

        con = sqlite3.connect('results.bd')
        cur = con.cursor()
        self.result = cur.execute("""SELECT * FROM results
                                    WHERE result > 0""").fetchall()
        self.out_res()

    def out_res(self):

        res_table = []
        for i in self.result:
            res_table.append(str(*i))
        self.label_res.setText('\n'.join(res_table))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = GameStartWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
