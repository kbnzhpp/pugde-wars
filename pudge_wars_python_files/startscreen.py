import pygame
from config import *
from classes import *
import sys
import random as rd
from connect_screen import *
from font_change import *

def startscreen(screen):
    """Start screen func"""
    pygame.init()
    pygame.display.set_caption('dota 3')
    clock = pygame.time.Clock()
    players = pygame.sprite.Group()
    start_screen = True
    
    font_config = pygame.font.Font(None, 25)
    bg_surf = pygame.image.load("data/images/start_bg.jpeg").convert()
    bg_surf = pygame.transform.scale(bg_surf, (screen.get_width(), screen.get_height()))
    font_start = pygame.font.Font('data/Fonts/Jost-Bold.ttf', 60)
    font_button_skin_panel = pygame.font.Font('data/Fonts/Jost-Bold.ttf', 40)
    rect_header = pygame.rect.Rect(0, 0, WIDTH, 200)
    start_text = textOutline(font_start, "PUDGE WARS", (81, 255, 149), (44, 44, 44))
    start_rect = start_text.get_rect(center=rect_header.center)
    skins = lambda: ('skins')
    conn = lambda: ('connect')
    serv = lambda: ('server')
    button_skins = Button(  
        1300,
        200,
        400,
        HEIGHT - 300,
        (112, 128, 144),
        (129, 146, 163),
        font_button_skin_panel, 
        skins,
        None,
        "СКИНЫ",
        (20, 20, 20),
        volume = False,
        )
    button_connect = Button(  
        WIDTH / 2 - 200,
        200,
        400,
        HEIGHT - 300,
        (112, 128, 144),
        (129, 146, 163),
        font_button_skin_panel, 
        conn,
        None,
        "ПОДКЛЮЧИТЬСЯ",
        (20, 20, 20),
        volume = False
        )
    button_start_server = Button(  
        200,
        200,
        400,
        HEIGHT - 300,
        (112, 128, 144),
        (129, 146, 163),
        font_button_skin_panel, 
        serv,
        None,
        "СОЗДАТЬ СЕРВЕР",
        (20, 20, 20),
        volume = False
        )
    config = [
            'Параметры:', 
            'Ходить - WASD', 
            'Хук - Q', 
            'Радиус хука - ALT', 
            'Выйти в главное меню - ESC + ENTER'
            ]
    
    # Инициализация стартового экрана
    while start_screen:
        screen.blit(bg_surf, (0, 0))
        screen.blit(start_text, start_rect)
        button_skins.draw(screen)
        button_connect.draw(screen)
        button_start_server.draw(screen)

        for i, string in enumerate(config):
            a = font_config.render(string, True, (255, 255, 255))
            screen.blit(a, (10, 10 + i * 20))
        
        res_butt_skins = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            res_butt_skins = button_skins.click(e)
            if res_butt_skins:
                return res_butt_skins
            res_butt_conn = button_connect.click(e)
            if res_butt_conn:
                return res_butt_conn
            res_butt_serv = button_start_server.click(e)
            if res_butt_serv:
                return res_butt_serv
        
        pygame.display.update()
        clock.tick(60)
    pygame.quit()
    sys.exit()