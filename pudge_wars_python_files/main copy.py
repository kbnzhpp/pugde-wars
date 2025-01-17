import pygame
from config import *
from classes import *
from connect_screen import connect_screen
from skins_panel_screen import skins_screeen
from connect_screen import connect_screen
from startscreen import startscreen
from start_server_screen import start_server_screen
from client import main

def main_loop():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("dota 3")
    clock = pygame.time.Clock()

    players = pygame.sprite.Group()
    current_screen = "start"
    sock = None
    local_player = None
    skin_pudge, skin_hook = 'default', 'default'

    while True:
        print(current_screen)

        if current_screen == "start":
            # Главное меню
            current_screen = startscreen(screen)

        if current_screen == "server":   
            # Экран создания сервера
            result = start_server_screen(screen, players, skin_pudge, skin_hook)
            if result is None:  # Возврат в главное меню
                current_screen = "start"
            else:
                sock, local_player, game, players = result
                current_screen = game

        if current_screen == "skins":
            # Экран выбора скинов
            current_screen, skin_pudge, skin_hook = skins_screeen(screen)
        if current_screen == "connect":
            # Экран подключения
            result = connect_screen(screen, players, skin_pudge, skin_hook)
            if result is None:  # Возврат в главное меню
                current_screen = "start"
            else:
                sock, local_player, game, players = result
                current_screen = game

        if current_screen == "game":
            # Игровой процесс
            current_screen = main(screen, sock, local_player, True, players)
        clock.tick(60)

if __name__ == '__main__':
    main_loop()