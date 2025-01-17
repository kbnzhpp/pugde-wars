import pygame
from config import *
from classes import *
import sys
from client import *
from config import skins_hook, skins_pudge
from connect import connect_to_server
from font_change import *

def connect_screen(screen, players, skin_pudge, skin_hook):
    ip = ''
    pygame.init()
    #screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('dota 3')
    bg_surf = pygame.image.load("data/images/start_bg.jpeg").convert()
    bg_surf = pygame.transform.scale(bg_surf, (screen.get_width(), screen.get_height()))
    font_header = pygame.font.Font('data/Fonts/Jost-Bold.ttf', 60)
    font_start = pygame.font.Font(None, 40)
    font_ip = pygame.font.Font('data/Fonts/InterTight-Bold.ttf', 45)
    clock = pygame.time.Clock()
    # Initialize players group at start
    print(f"[DEBUG] Players group created: {players}")
    stop = False
    connectscreen = True
    header_text = textOutline(font_header, 'ПОДКЛЮЧИТЬСЯ К СЕРВЕРУ', (255, 165, 0), (40, 40, 40))
    header_rect = header_text.get_rect(center = pygame.rect.Rect(0, 0, WIDTH, 200).center)
    while connectscreen:
        ip_text = font_ip.render(ip, True, (0, 0, 0))
        ip_rect = ip_text.get_rect(center = pygame.rect.Rect(0, 0, WIDTH, 400).center)
        screen.blit(bg_surf, (0,0))
        screen.blit(ip_text, ip_rect)
        screen.blit(header_text, header_rect)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    stop = True
                elif e.key == pygame.K_BACKSPACE:
                    ip = ip[:-1]
                elif e.unicode.isprintable():  # Добавляем только печатные символы
                    ip += e.unicode
                if e.key == pygame.K_ESCAPE:  # Возврат в главное меню
                    return None # Завершаем экран подключения
        pygame.display.update()

        if ip != '' and stop:
            last_ip = ip
            if ip == 'pipindrik' and 'amogus' not in skins_pudge.keys():
                skins_pudge['amogus'] = pygame.image.load('data/images/pudge_amogus_right.png')
                congrats_text = font_start.render("ПОЗДРАВЛЯЕМ! ВЫ ПОЛУЧИЛИ НАГРАДУ", True, (15, 255, 20))
                screen.blit(congrats_text, (0,0))
                pygame.display.update()
                ip = ''
                stop = False
                pygame.time.wait(700)
                continue
            try:    
                sock, local_player = connect_to_server(players, ip, skin_pudge, skin_hook)
                if sock == local_player == None:
                    raise Exception 
            except Exception:
                error_text = font_start.render("ВВЕДЕН НЕВЕРНЫЙ IP:", True, (255, 0, 0))
                screen.blit(error_text, (0,0))
                pygame.display.update()
                ip = ''
                stop = False
                pygame.time.wait(1000)
            else:
                ip = ''
                stop = False
                return sock, local_player, 'game', players

        clock.tick(60)