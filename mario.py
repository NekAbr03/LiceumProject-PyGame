import json
import random
import sqlite3
import sys
from play import play
from copy import copy
from scipy.ndimage.filters import *
import pygame
from pygame import mixer, K_LEFT, K_h, K_RIGHT, K_l, K_SPACE, K_UP, K_k, K_LSHIFT
from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import *
from pygame.display import flip


class GameStartWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.font = QFont()
        uic.loadUi('untitled.ui', self)
        self.setStyleSheet(
            'QWidget { background-color: rgb(30, 31, 38);}'
            'QPushButton { background-color: rgb(30, 31, 38); color: rgb(255, 255, 255);}'
            'QLabel { color: rgb(255, 255, 255);}'
            'QWidget {font-family: "comfortaa";}'
            'QPushButton { font-family: "comfortaa";}')
        self.font.setPointSize(15)
        self.font.setBold(True)
        self.button_exit.setText('Выйти')
        self.button_exit.clicked.connect(self.close_window)
        self.button_exit.setFont(self.font)
        self.button_exit.setIcon(QIcon('data/Exit_Button.png'))
        self.button_exit.setIconSize(QSize(171, 51))
        self.button_exit.setText('')

        self.button_music.setFont(self.font)
        self.button_music.clicked.connect(self.music)
        self.button_music.setVisible(False)

        self.button_rez.clicked.connect(self.open_result)

        self.button_play.setIcon(QIcon('data/Play_Button.png'))
        self.button_play.setText('')
        self.button_play.setIconSize(QSize(431, 161))
        self.button_play.clicked.connect(self.play)

        self.button_rez.setIcon(QIcon('data/Results_Button.png'))
        self.button_rez.setIconSize(QSize(431, 161))
        self.button_rez.setText('')

        self.pic_background = QPixmap('data/Mario_Background.jpg')
        self.label_main.setPixmap(self.pic_background)

    def close_window(self):
        self.close()

    def play(self):
        self.w = play()
        self.w.play()

    def open_result(self):  # окно с таблицей результатов
        self.window_res = Results()
        self.window_res.show()

    def update_res(self):  # обновление результата в label_rez
        pass

    def music(self):
        pass


class Results(QWidget):
    def __init__(self):
        super().__init__()
        self.font = QFont()
        self.setObjectName('window_res')

        self.setGeometry(1460, 185, 500, 500)
        self.setWindowTitle("Результаты")

        self.button_close_res = QPushButton(self)
        self.button_close_res.resize(150, 50)
        self.button_close_res.move(350, 430)
        self.button_close_res.setText('Закрыть')
        self.button_close_res.clicked.connect(self.close_res)

        self.label_res = QLabel(self)
        self.label_res.resize(640, 480)

        con = sqlite3.connect('results.db')
        cur = con.cursor()
        self.result = cur.execute("""SELECT * FROM rezults
                                    WHERE rezult > 0""").fetchall()
        self.out_res()

    def close_res(self):
        self.close()

    def out_res(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = GameStartWidget()
    form.show()
    sys.exit(app.exec())

