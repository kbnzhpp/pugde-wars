import pygame
from config import *
from player import Player
import socket
import pickle

def serialize_player_data(player):
    """Создает словарь только с сериализуемыми данными игрока"""
    return {
        "id": id(player),
        "x": player.hitbox.x,
        "y": player.hitbox.y,
        "team": player.team,
        "hook_active": player.hook.active,
        "hook_returning": player.hook.returning,
        "alive": player.alive,
        "hook_x": player.hook.rect.x if player.hook.active or player.hook.returning else None,
        "hook_y": player.hook.rect.y if player.hook.active or player.hook.returning else None
    }

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('dota 3')

    clock = pygame.time.Clock()

    # Подключение к серверу
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("192.168.1.135", 5555))
        sock.settimeout(0.1)
        print("Успешно подключились к серверу")
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу")
        return

    players = pygame.sprite.Group()
    local_player = Player(340, 200, players, team=1)
    local_player.id_p = 1  # Установим уникальный ID для локального игрока
    players.add(local_player)  # Явно добавляем его в группу
    
    def reset_game():
        nonlocal team_kills, players
        team_kills = {1: 0, 2: 0}
        players.empty()
        # Recreate all players with unique IDs
        player_1 = Player(340, 200, players, 1)
        player_1.id_p = 1  # Это будет наш local_player
        player_2 = Player(340, 500, players, 1)
        player_2.id_p = 2
        player_3 = Player(340, 800, players, 1)
        player_3.id_p = 3
        player_4 = Player(1620, 200, players, 2)
        player_4.id_p = 4
        player_5 = Player(1620, 500, players, 2)
        player_5.id_p = 5
        player_6 = Player(1620, 800, players, 2)
        player_6.id_p = 6
        return player_1  # Return a reference to local player
    
    local_player = reset_game()  # Теперь local_player будет иметь правильный ID и позицию
    
    team_kills = {
        1: 0, 
        2: 0
    }

    bg_surf = pygame.image.load("data/images/background.jpg").convert()
    bg_surf = pygame.transform.scale(bg_surf, (screen.get_width(), screen.get_height()))
    screen.blit(bg_surf, (0,0)) 

    center_rect = pygame.Rect((714, 0, 400, HEIGHT))
    center_surf = pygame.Surface((400, HEIGHT))
    center_surf.set_alpha(0)
    screen.blit(center_surf, center_rect) 
    
    left = right = up = down = show_hook_radius = False

    game_over = False
    winning_team = None
    win_display_timer = 0

    while True:
        clock.tick(FPS) # fps change
        
        screen.blit(bg_surf, (0,0))     
        screen.blit(center_surf, center_rect) 

        # Обновление игрока
        local_player.move(left, right, up, down, center_rect, players)
        local_player.hook.move(players, team_kills)
        
        # Отрисовка
        screen.blit(bg_surf, (0,0))     
        screen.blit(center_surf, center_rect) 

        # Отладочная информация
        print(f"Количество игроков в группе: {len(players)}")
        print(f"Позиция local_player: {local_player.rect.center}")
        
        # Отрисовка всех игроков
        for player in players:
            print(f"Отрисовка игрока: {player.id_p} на позиции {player.rect.center}")
            if player.alive:
                screen.blit(player.image, player.rect)
            if player.hook.active or player.hook.returning:
                player.hook.draw_chain(screen)
                screen.blit(player.hook.image, player.hook.rect)
        
        # Отрисовка радиуса крюка
        if show_hook_radius:
            pygame.draw.circle(screen, (0,255,0), local_player.rect.center, HOOK_RADIUS, 1)
        
        pygame.draw.rect(screen, (255, 0, 0), local_player.rect, 2)  # Красный прямоугольник вокруг игрока
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # client.sock.close()
                exit()

            if event.type >= pygame.USEREVENT:
                # Check if the event is a respawn event for a specific player
                for player in players:
                    event_type = pygame.USEREVENT + (player.id_p % 1000)
                    if event.type == event_type:
                        player.respawn()
                        pygame.time.set_timer(event_type, 0)  # Disable the timer after triggering

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
                    if local_player.hook.active or local_player.hook.returning:
                        continue
                    local_player.hook.launch(pygame.mouse.get_pos())
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
        
        for team, kills in team_kills.items():
            if kills >= WIN_CONDITION:
                game_over = True
                winning_team = team
                win_display_timer = pygame.time.get_ticks()
                break

        if game_over:
            # Display the winning message
            font = pygame.font.Font(None, 100)
            message = f"Team {winning_team} Wins!"
            text = font.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(bg_surf, (0, 0))  # Redraw background
            screen.blit(text, text_rect)

            pygame.display.update()

            # Restart the game after a delay
            if pygame.time.get_ticks() - win_display_timer > 3000:  # 3 seconds
                game_over = False
                player_1 = reset_game()
            continue

        # Отправка данных на сервер
        try:
            player_data = serialize_player_data(local_player)
            sock.sendall(pickle.dumps(player_data))
            
            # Получение данных от сервера
            data = sock.recv(4096)
            game_state = pickle.loads(data)
            
            # Обновление состояния игроков
            if "players" in game_state:
                current_players = {id(p): p for p in players}
                players.empty()
                
                for p_data in game_state["players"]:
                    if p_data["id"] != id(local_player):
                        # Создаем нового игрока или используем существующего
                        if p_data["id"] in current_players:
                            player = current_players[p_data["id"]]
                            player.hitbox.x = p_data["x"]
                            player.hitbox.y = p_data["y"]
                        else:
                            player = Player(p_data["x"], p_data["y"], players, p_data["team"])
                        
                        player.alive = p_data["alive"]
                        player.hook.active = p_data["hook_active"]
                        player.hook.returning = p_data["hook_returning"]
                        
                        # Обновляем позицию крюка
                        if p_data["hook_x"] is not None and p_data["hook_y"] is not None:
                            player.hook.rect.x = p_data["hook_x"]
                            player.hook.rect.y = p_data["hook_y"]
                        
                        players.add(player)
                
                players.add(local_player)
                
        except (socket.timeout, EOFError, pickle.UnpicklingError) as e:
            print(f"Ошибка сети: {e}")
            pass

        # Отрисовка
        screen.blit(bg_surf, (0,0))     
        screen.blit(center_surf, center_rect) 

        for player in players:
            if player.alive:
                screen.blit(player.image, player.rect)
            if player.hook.active or player.hook.returning:
                player.hook.draw_chain(screen)
                screen.blit(player.hook.image, player.hook.rect)
        
        pygame.draw.rect(screen, (255, 0, 0), local_player.rect, 2)  # Красный прямоугольник вокруг игрока
        
        pygame.display.flip()

if __name__ == '__main__':
    main()

