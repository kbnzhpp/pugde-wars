import pygame
from config import *
from classes import *
import socket
import sys
from connect import connect_to_server
from server import GameServer
import subprocess
import os
import time

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname (hostname)
    return local_ip

def start_server_screen(screen, players, skin_pudge, skin_hook):
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('dota 3')
    bg_surf = pygame.image.load("data/images/start_bg.jpeg").convert()
    bg_surf = pygame.transform.scale(bg_surf, (screen.get_width(), screen.get_height()))
    font = pygame.font.Font(None, 70)
    start_server = True
    
    while start_server:
        screen.blit(bg_surf, (0, 0))
        
        try:
            # Start server
            subprocess.Popen(['start_server.bat'], shell=True)
            # Try to connect
            ip = get_local_ip()
            print(ip)
            sock, player = connect_to_server(players, ip, skin_pudge, skin_hook)
            if sock and player:
                return sock, player, 'game', players
                
        except Exception as e:
            print(f"[ERROR] Server start failed: {e}")
            
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return None
                
        pygame.display.update()
        clock.tick(60)
