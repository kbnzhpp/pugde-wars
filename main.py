import pygame
from config import *
from player import Player

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('dota 3')

    clock = pygame.time.Clock()

    players = pygame.sprite.Group()
    player_1 = Player(340, 200, players)
    player_2 = Player(340, 500, players)
    player_3 = Player(340, 800, players)
    player_4 = Player(1620, 200, players)
    player_5 = Player(1620, 500, players)
    player_6 = Player(1620, 800, players)
    team_1 = pygame.sprite.Group()
    team_2 = pygame.sprite.Group()

    bg_surf = pygame.image.load("data/images/background.jpg").convert()
    bg_surf = pygame.transform.scale(bg_surf, (screen.get_width(), screen.get_height()))
    screen.blit(bg_surf, (0,0)) 

    center_rect = pygame.Rect((714, 0, 400, HEIGHT))
    center_surf = pygame.Surface((400, HEIGHT))
    center_surf.set_alpha(0)
    screen.blit(center_surf, center_rect) 
    
    left = right = up = down = show_hook_radius = False
    while True:
        clock.tick(FPS) # fps change

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # client.sock.close()
                exit()
            if event.type == pygame.KEYDOWN: # Движение
                if event.key == ord('w'):
                    up = True
                if event.key == ord('a'):
                    left = True
                if event.key == ord('s'):
                    down = True
                if event.key == ord('d'):
                    right = True
                if event.key == ord('q'):
                    if player_3.hook.active or player_3.hook.returning:
                        continue
                    player_3.hook.launch(pygame.mouse.get_pos())
                if event.key == pygame.K_LALT:
                    show_hook_radius = True

            if event.type == pygame.KEYUP: # Остановка движения
                if event.key == ord('w'):
                    up = False
                if event.key == ord('a'): 
                   left = False
                if event.key == ord('s'):
                    down = False
                if event.key == ord('d'):
                    right = False
                if event.key == pygame.K_LALT:
                    show_hook_radius = False
        
        screen.blit(bg_surf, (0,0))     
        screen.blit(center_surf, center_rect) 
        players.draw(screen)
        
        player_3.move(left, right, up, down, center_rect, players)
        
        player_3.hook.move(players)
        if player_3.hook.active or player_3.hook.returning:
            player_3.hook.draw_chain(screen)
            screen.blit(player_3.hook.image, player_3.hook.rect)
        
        if show_hook_radius:
            pygame.draw.circle(screen, (0,255,0), player_3.rect.center, HOOK_RADIUS, 1)

        pygame.display.update() # updating display

if __name__ == '__main__':
    main()

