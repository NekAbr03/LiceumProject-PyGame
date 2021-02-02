import sys
import sqlite3
import os
import sys
import random
import pygame
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5 import uic
from PyQt5.QtWidgets import *


class GameStartWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.font = QFont()
        uic.loadUi('untitled.ui', self)
        self.setStyleSheet('QWidget { background-color: rgb(30, 31, 38);}'
                           'QPushButton { background-color: rgb(30, 31, 38); color: rgb(255, 255, 255);}'
                           'QLabel { color: rgb(255, 255, 255);}'
                           'QWidget {font-family: "comfortaa";}'
                           'QPushButton { font-family: "comfortaa";}'
                           )
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
        PLay()

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

        self.setGeometry(1460, 185, 500, 500)
        self.setWindowTitle("Результаты")

        self.button_close_res = QPushButton(self)
        self.button_close_res.resize(150, 50)
        self.button_close_res.move(350, 430)
        self.button_close_res.setText('Закрыть')

        self.label_res = QLabel(self)
        self.label_res.resize(500, 450)

        con = sqlite3.connect('results.db')
        cur = con.cursor()
        self.result = cur.execute("""SELECT * FROM rezults
                                    WHERE rezult > 0""").fetchall()
        self.out_res()

    def out_res(self):
        res_table = []
        for i in self.result:
            res_table.append(str(*i))
        self.label_res.setText('\n'.join(res_table))



class PLay(GameStartWidget):
    pygame.init()
    size = width, height = 750, 500
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    if __name__ == '__main__':

        # создадим группу, содержащую все спрайты
        all_sprites = pygame.sprite.Group()
        running = True
        while running:
            # внутри игрового цикла ещё один цикл
            # приема и обработки сообщений
            for event in pygame.event.get():
                # при закрытии окна
                if event.type == pygame.QUIT:
                    running = False
            screen.fill(pygame.Color("black"))
            all_sprites.draw(screen)
            all_sprites.update()
            clock.tick(50)
            # обновление экрана
            pygame.display.flip()
        pygame.quit()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = GameStartWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
