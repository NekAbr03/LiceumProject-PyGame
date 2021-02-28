import pygame
import entities
import clases


windowSize = 640, 480


def play():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()


    screen = pygame.display.set_mode(windowSize)
    max_frame_rate = 60
    dashboard = clases.Dashboard("./data/font.png", 8, screen)
    sound = clases.Sound()
    level = clases.Level(screen, sound, dashboard)
    menu = clases.Menu(screen, dashboard, level, sound)

    while not menu.start:
        menu.update()

    mario = entities.Mario(0, 0, level, screen, dashboard, sound)
    clock = pygame.time.Clock()

    while not mario.restart:
        if mario.pause:
            mario.pauseObj.update()
        else:
            level.drawLevel(mario.camera)
            dashboard.update()
            mario.update()
        pygame.display.update()
        clock.tick(max_frame_rate)
    return 'restart'

if __name__ == "__main__":
    exitmessage = 'restart'
    while exitmessage == 'restart':
        exitmessage = play()
