import pygame
from config import *
from classes import *
import sys
import random as rd
from connect_screen import *

def skins_screeen(screen):
    pygame.init()
    clock = pygame.time.Clock()

    bg_surf = pygame.image.load("data/images/start_bg.jpeg").convert()
    bg_surf = pygame.transform.scale(bg_surf, (screen.get_width(), screen.get_height()))
    font_skin_panel = pygame.font.Font(None, 39)
    skin_panel = SkinPanel(skins_pudge, skins_hook, font_skin_panel, 'СКИНЫ', 530, 550)
    skin_pudge = skin_panel.selected_player_skin
    skin_hook = skin_panel.selected_hook_skin
    skinspanel = True
    skin_panel.open = True

    while skinspanel:
        screen.blit(bg_surf, (0, 0))
          # Открываем панель только один раз, если это нужно
        skin_panel.draw_panel(screen)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: 
                    return 'start', skin_pudge, skin_hook
            
            if skin_panel.open:  # Add this check
                skin_panel.handle_event(e)
                  # Add event handling
        skin_pudge = skin_panel.selected_player_skin
        skin_hook = skin_panel.selected_hook_skin

        pygame.display.update()
        clock.tick(60)

    return skin_pudge, skin_hook