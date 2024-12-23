import pygame
from config import *
from player import Player
import socket
import pickle
import sys

"26.140.237.173"
def serialize_player_data(player):
    """Создает словарь с данными игрока"""
    if player.hook.hit_player_id is not None:
        target_player = next((p for p in player.groups()[0] if p.id_p == player.hook.hit_player_id), None)
        if target_player and (target_player.invulnerable or not target_player.alive):
            player.hook.hit_player_id = None
            
    data = {
        "id": player.id_p,
        "x": int(player.rect.centerx),
        "y": int(player.rect.centery),
        "team": player.team,
        "alive": player.alive,
        "respawn_timer": player.respawn_timer,
        "hook_active": player.hook.active if player.alive else False,
        "hook_returning": player.hook.returning if player.alive else False,
        "hook_x": int(player.hook.rect.centerx) if (player.hook.active or player.hook.returning) and player.alive else None,
        "hook_y": int(player.hook.rect.centery) if (player.hook.active or player.hook.returning) and player.alive else None,
        "hook_hit_player": player.hook.hit_player_id if hasattr(player.hook, 'hit_player_id') else None
    }
    return data

def get_spawn_position(player_id):
    """Возвращает позицию спавна и команду на основе ID игрока"""
    spawns = {
        1: {"pos": (340, 200), "team": 1},
        2: {"pos": (1620, 200), "team": 2}, 
        3: {"pos": (340, 500), "team": 1},
        4: {"pos": (1620, 500), "team": 2}, 
        5: {"pos": (340, 800), "team": 1}, 
        6: {"pos": (1620, 800), "team": 2}
    }
    
    # Если ID больше 6, используем циклическое распределение
    actual_id = ((player_id - 1) % 6) + 1
    return spawns[actual_id]

def reset_game():
    """Инициализация игровых объектов"""
    global center_rect
    center_rect = pygame.Rect(WIDTH // 2 - 50, 0, 100, HEIGHT)
    return center_rect

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('dota 3')
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])  # Разрешаем только нужные события
    
    clock = pygame.time.Clock()
    players = pygame.sprite.Group()
    local_player = None
    other_players = {}
    
    # Инициализация игровых объектов
    center_rect = reset_game()
    
    # Подключение к серверу
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("26.140.237.173", 5555))
        sock.settimeout(0.1)
        
        # Получаем свой ID от сервера
        data = sock.recv(4096)
        init_data = pickle.loads(data)
        if "your_id" in init_data:
            player_id = init_data["your_id"]
            print(f"[INIT] Получен ID от сервера: {player_id}")
            
            # Создаем локального игрока
            spawn_data = get_spawn_position(player_id)
            local_player = Player(spawn_data["pos"][0], spawn_data["pos"][1], players, spawn_data["team"])
            local_player.set_id(player_id)
            players.add(local_player)
            print(f"[INIT] Создан локальный игрок с ID={local_player.id_p}")
        else:
            print("[ERROR] Не получен ID от сервера")
            return

        print(f"[DEBUG] ID локального игрока после создания: {local_player.id_p}")
        print("Успешно подключились к серверу")
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу")
        return

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

    # Добавляем отрисовку счета
    def draw_score():
        font = pygame.font.Font(None, 36)
        team1_text = font.render(f"Team 1: {team_kills[1]}", True, (255, 0, 0))
        team2_text = font.render(f"Team 2: {team_kills[2]}", True, (0, 0, 255))
        screen.blit(team1_text, (10, 10))
        screen.blit(team2_text, (WIDTH - 150, 10))

    # Инициализация перед основным циклом
    team_kills = {1: 0, 2: 0}  # Начальные значения
    game_state = {}  # Инициализируем пустой game_state
    
    try:
        while True:
            clock.tick(FPS)
            
            # Отрисовка
            screen.blit(bg_surf, (0,0))     
            screen.blit(center_surf, center_rect) 
            
            # Отрисовка всех игроков
            for player in players:
                if player.alive:  # Отрисовываем только живых игроков
                    screen.blit(player.image, player.rect)
                if player.hook.active or player.hook.returning:
                    player.hook.draw_chain(screen)
                    screen.blit(player.hook.image, player.hook.rect)
            
            # Отрисовка радиуса крюка
            if show_hook_radius and local_player.alive:
                pygame.draw.circle(screen, (0,255,0), local_player.rect.center, HOOK_RADIUS, 1)
            
            if local_player.alive:
                pygame.draw.rect(screen, (255, 0, 0), local_player.hitbox, 2)  # Красный прямоугольник вокруг игрока
            
            draw_score()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Отправляем сигнал отключения
                    disconnect_data = {"disconnect": True, "id": local_player.id_p}
                    try:
                        sock.sendall(pickle.dumps(disconnect_data))
                    except:
                        pass
                    finally:
                        # Очищаем ресурсы без вызова kill()
                        for player in players:
                            player.alive = False  # Просто отмечаем как неживого
                        players.empty()
                        other_players.clear()
                        sock.close()
                        pygame.quit()
                        print("Игра завершена")
                        sys.exit()
                        
                if event.type == pygame.WINDOWFOCUSLOST:
                    continue
                
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
                        if local_player and not local_player.hook.active and not local_player.hook.returning:
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
            
            # Обновление всех игроков
            if local_player:
                local_player.update()
                if local_player.alive:
                    local_player.move(left, right, up, down, center_rect, players)
                local_player.hook.update()
                
            # Обновляем других игроков
            for player in other_players.values():
                player.update()  # Вызываем update для обработки респавна
                if player.hook.active or player.hook.returning:
                    player.hook.update()

            for team, kills in team_kills.items():
                if kills >= WIN_CONDITION:
                    game_over = {"game_over" : True}
                    sock.sendall(pickle.dumps(game_over))

                    #winning_team = team
                    #win_display_timer = pygame.time.get_ticks()  # Инициализируем локально
                    ## Отправляем сигнал о победе на сервер
                    #win_data = {
                    #    "game_win": True,
                    #    "winning_team": team,
                    #    "win_time": win_display_timer
                    #}
                    #sock.sendall(pickle.dumps(win_data))
                    #print(f"[DEBUG] Отправляем сигнал о победе на сервер")
                    #break

            if "game_over" in game_state and game_state["game_over"]:
                print(f"[DEBUG] game_over: {game_over}, game_state: {game_state}")
                
                font = pygame.font.Font(None, 100)
                message = f"Team {winning_team} Wins!"
                text = font.render(message, True, (255, 255, 255))
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                
                screen.blit(text, text_rect)
                
                # Отправляем сигнал для рестарта игры
                restart_data = {"restart_game": True}
                sock.sendall(pickle.dumps(restart_data))
                
                print(f"[DEBUG] Отправляем сигнал для рестарта игры")
                # Сбрасываем все переменные
                game_over = False
                team_kills = {1: 0, 2: 0}
                game_state = {}
                
                # Респавним локального игрока
                spawn_data = get_spawn_position(local_player.id_p)
                local_player.rect.center = spawn_data["pos"]
                local_player.alive = True
                local_player.respawn_timer = 0

            pygame.display.update()

            # Отправка и получение данных
            try:
                # Отправляем только свои данные
                player_data = serialize_player_data(local_player)
                sock.sendall(pickle.dumps(player_data))
                
                try:
                    data = sock.recv(4096)
                    if data:
                        try:  # Добавляем обработку ошибки здесь
                            game_state = pickle.loads(data)
                            if isinstance(game_state, dict):
                                # Обновляем team_kills из данных сервера
                                if "team_kills" in game_state:
                                    team_kills = game_state["team_kills"]
                                else:
                                    print("[DEBUG] team_kills отсутствует в данных сервера")
                                
                                if "players" in game_state:
                                    # Получаем список активных ID
                                    active_ids = {p_data["id"] for p_data in game_state["players"]}
                                    
                                    # Удаляем отключившихся игроков
                                    disconnected_ids = set(other_players.keys()) - active_ids
                                    for player_id in disconnected_ids:
                                        if player_id in other_players:
                                            other_players[player_id].hook.kill()  # Удаляем хук
                                            other_players[player_id].kill()       # Удаляем игрока
                                            del other_players[player_id]
                                            print(f"[DISCONNECT] Игрок {player_id} отключился")

                                    
                                    # Обновляем других игроков
                                    for p_data in game_state["players"]:
                                        # Проверяем попадание в локального игрока
                                        
                                        if (p_data["hook_hit_player"] is not None and 
                                            p_data["hook_hit_player"] == local_player.id_p and 
                                            local_player.alive and 
                                            not local_player.invulnerable):
                                            local_player.last_hit_by = p_data["id"]  # Сохраняем ID убийцы
                                            local_player.kill()
                                            
                                            # Отправляем обновленное состояние на сервер немедленно
                                            update_data = serialize_player_data(local_player)
                                            sock.sendall(pickle.dumps(update_data))
                                            
                                            # Отправляем информацию о килле отдельным пакетом
                                            killer_data = {
                                                "kill_event": True,
                                                "killer_id": local_player.last_hit_by,
                                                "victim_id": local_player.id_p
                                            }
                                            sock.sendall(pickle.dumps(killer_data))
                                            continue  # Пропускаем текущий цикл и начинаем новый для получения обновленных данных
                                        
                                        if p_data["id"] != local_player.id_p:
                                            if p_data["id"] not in other_players:
                                                spawn_data = get_spawn_position(p_data["id"])
                                                new_player = Player(p_data["x"], p_data["y"], players, spawn_data["team"])
                                                new_player.set_id(p_data["id"])
                                                other_players[p_data["id"]] = new_player
                                                players.add(new_player)
                                                print(f"[CONNECT] Новый игрок {p_data['id']}")
                                            else:
                                                player = other_players[p_data["id"]]
                                                
                                                # Синхронизируем состояние alive
                                                player.alive = p_data["alive"]
                                                # Проверяем попадание в других игроко��
                                                if (p_data["hook_hit_player"] is not None and 
                                                    p_data["hook_hit_player"] == player.id_p and 
                                                    player.alive and 
                                                    not player.invulnerable):
                                                    player.last_hit_by = p_data["id"]  # Сохраняем ID убийцы
                                                    player.kill()
                                                    player.hook.hit_player_id = None  # Очищаем hit_player_id
                                                
                                                if not player.alive:
                                                    # Если игрок мертв, убираем его хук
                                                    player.hook.active = False
                                                    player.hook.returning = False
                                                    player.hook.rect.center = player.rect.center
                                                else:
                                                    # Обновляем позицию только живых игроков
                                                    player.rect.center = (p_data["x"], p_data["y"])
                                                    player.hitbox.center = player.rect.center
                                                    
                                                    # Обновляем хук только для живых игроков
                                                    player.hook.active = p_data["hook_active"]
                                                    player.hook.returning = p_data["hook_returning"]
                                                    if player.hook.active or player.hook.returning:
                                                        player.hook.rect.center = (p_data["hook_x"], p_data["hook_y"])
                        except KeyError:  # Игнорируем ошибку отсутствия ключа
                            pass
                except socket.timeout:
                    pass

            except Exception as e:
                print(f"Ошибка отправки данных: {e}")

    except Exception as e:
        print(f"[ERROR] Ошибка в главном цикле: {e}")
    finally:
        # Гарантируем очистку даже при ошибках
        try:
            if local_player and local_player.id_p:
                disconnect_data = {"disconnect": True, "id": local_player.id_p}
                sock.sendall(pickle.dumps(disconnect_data))
        except:
            pass
        finally:
            for player in players:
                player.kill()
            players.empty()
            other_players.clear()
            sock.close()
            pygame.quit()
    
if __name__ == '__main__':
    main()
