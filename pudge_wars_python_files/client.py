import pygame
from config import *
from classes import *
import socket
import pickle
import sys
import random as rd
import subprocess
from player import *

def serialize_player_data(player):
    """Создает словарь с данными игрока"""
    if player.hook.hit_player_id is not None:
        target_player = next((p for p in player.groups()[0] if p.id_p == player.hook.hit_player_id), None)
        if target_player and not target_player.alive:
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
        "hook_hit_player": player.hook.hit_player_id if hasattr(player.hook, 'hit_player_id') else None,
        'hook_direction': player.hook.direction,
        'player_direction': player.direction,
        'skin_player': player.skin,
        'skin_hook': player.hook.skin
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
    if actual_id % 2 == 0:
        return rd.choice([spawns[2], spawns[4], spawns[6]])
    else:
        return rd.choice([spawns[1], spawns[3], spawns[5]])

def reset_game():
    """Инициализация игровых объектов"""
    center_rect = pygame.Rect(WIDTH // 2 - 50, 0, 100, HEIGHT)
    return center_rect

def main(screen, sock, local_player, game, players):
    """Main function of game"""
    def draw_hud(local_player):
        font = pygame.font.Font(None, 50)
        team1_text = font.render(f"БАРЕБУХИ: {team_kills[1]}", True, (0, 250, 154))
        team2_text = font.render(f"АБАЛДУИ: {team_kills[2]}", True, (255, 228, 181))
        fps = font.render(f"FPS: {clock.get_fps():.2f}", True, (255, 255, 255))
        hook_cooldown_time = font.render(str(int(HOOK_COOLDOWN / 1000 - local_player.hook.timer // 1000)), True, (255, 255, 255)) if local_player.hook.cooldown != 0 else font.render('', True, (255, 255, 255))
        hook_cooldown_image = pygame.image.load('data/images/hook_skill_image.png') if local_player.hook.cooldown == 0 else pygame.image.load('data/images/hook_skill_image_dark.png')

        scoreboard = pygame.Surface((WIDTH, 50))
        scoreboard.fill((50, 50, 50))

        skillboard = pygame.Surface((400, 100))
        skillboard.fill((50, 50, 50))

        screen.blit(scoreboard, (0, 0))
        screen.blit(skillboard, (WIDTH / 2 - 200, HEIGHT - 100))
        screen.blit(team1_text, (10, 10))
        screen.blit(team2_text, (WIDTH - 250, 10))
        screen.blit(fps, (WIDTH - 500, 10))
        screen.blit(hook_cooldown_image, (WIDTH / 2 - 190, HEIGHT - 90))
        screen.blit(hook_cooldown_time, (WIDTH / 2 - 162, HEIGHT - 70))

    pygame.init()
    pygame.display.set_caption('dota 3')
    
    clock = pygame.time.Clock()
    other_players = {}
    game = True

    bg_surf = pygame.image.load("data/images/background.jpg").convert()
    bg_surf = pygame.transform.scale(bg_surf, (screen.get_width(), screen.get_height()))
    center_rect = reset_game()
    screen.blit(bg_surf, (0,0)) 

    center_rect = pygame.Rect((714, 0, 400, HEIGHT))
    center_surf = pygame.Surface((400, HEIGHT))
    center_surf.set_alpha(0)
    screen.blit(center_surf, center_rect) 

    left = right = up = down = show_hook_radius = False

    # Инициализация перед основным циклом
    team_kills = {1: 0, 2: 0}  # Начальные значения
    game_state = {}  # Инициализируем пустой game_state
    if game_state and "game_over" in game_state:
        game_over = game_state["game_over"]
    else:
        game_over = False
    winning_team = None
    
    # Инициализация самой игры(соновного цикла)
    try:
        while game:
            # Отрисовка
            screen.blit(bg_surf, (0,0))     
            screen.blit(center_surf, center_rect) 
            # Отрисовка всех игроков
            for player in players:
                if player.alive:  # Отрисовываем только живых игроков
                    screen.blit(player.image, player.rect)
                    player.update()
                if player.hook.active or player.hook.returning:
                    player.hook.draw_chain(screen)
                    screen.blit(player.hook.image, player.hook.rect)

            # Отрисовка радиуса крюка
            if show_hook_radius and local_player.alive:
                pygame.draw.circle(screen, (0, 255, 0), local_player.rect.center, HOOK_RADIUS, 1)
            
            if local_player.alive:
                pygame.draw.polygon(screen, (40, 255, 40), 
                    [[local_player.rect.x + (local_player.rect.width / 2) - 12, local_player.rect.y - 50], [local_player.rect.x + (local_player.rect.width / 2) + 12, local_player.rect.y - 50], 
                     [local_player.rect.x + (local_player.rect.width / 2), local_player.rect.y - 20]])
            
            draw_hud(local_player)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                        
                if event.type == pygame.WINDOWFOCUSLOST:
                    continue
                
                if event.type == pygame.KEYDOWN:
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
                        fps = 0
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] and keys[pygame.K_RETURN]:
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
                return 'start'
            
            if local_player:
                local_player.update()
                if local_player.alive:
                    local_player.move(left, right, up, down, center_rect, players, clock.get_fps())    
                local_player.hook.update()
            for team, kills in team_kills.items():
                if kills >= WIN_CONDITION:
                    game_over = True
                    winning_team = team
                    win_data = {
                        'game_over' : game_over,
                        'winning_team' : winning_team
                    }
                    sock.sendall(pickle.dumps(win_data))
                    print(f"[DEBUG] Отправляем сигнал о победе на сервер")

            if game_over:
                # Отображаем экран победы
                font = pygame.font.Font(None, 100)
                if winning_team == 1:
                    message = "Команда баребухов победила!"
                elif winning_team == 2:
                    message = "Команда абалдуев победила!"
                text = font.render(message, True, (255, 255, 255))
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                
                # Добавляем сообщение о рестарте
                restart_font = pygame.font.Font(None, 50)
                restart_message = "Сервер перезапустится через 3 секунды..."
                restart_text = restart_font.render(restart_message, True, (255, 255, 255))
                restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
                
                # Отображаем сообщения
                screen.blit(bg_surf, (0,0))
                screen.blit(text, text_rect)
                screen.blit(restart_text, restart_rect)
                pygame.display.update()
                
                # Ждем 3 секунды и запускаем рестарт клиента
                pygame.time.wait(3000)
                
                subprocess.Popen(['client_restart.bat'], shell=True) # Запуск клиент
                break
            
            clock.tick(60)
            pygame.display.update()

            # Отправка и получение данных
            try:
                # Отправляем только свои данные
                player_data = serialize_player_data(local_player)
                sock.sendall(pickle.dumps(player_data))
                
                try:
                    data = sock.recv(16384)
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
                                            local_player.alive):
                                            local_player.last_hit_by = p_data["id"]  # Сохраняем ID убийцы
                                            local_player.kill()
                                            
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
                                                new_player = Player(p_data["x"], p_data["y"], players, spawn_data["team"], p_data['skin_player'], p_data['skin_hook'])
                                                new_player.set_id(p_data["id"])
                                                other_players[p_data["id"]] = new_player
                                                players.add(new_player)
                                                print(f"[CONNECT] Новый игрок {p_data['id']}")
                                            else:
                                                player = other_players[p_data["id"]]
                                                
                                                # Синхронизируем состояние alive
                                                player.alive = p_data["alive"]
                                                player.direction = p_data['player_direction']
                                                player.hook.direction = p_data['hook_direction']
                                                player.hook.image = pygame.image.load(f'data/images/hook_{player.hook.skin}_{player.hook.direction}.png') # Changed this line
                                                # Проверяем попадание в других игроков
                                                if (p_data["hook_hit_player"] is not None and 
                                                    p_data["hook_hit_player"] == player.id_p and 
                                                    player.alive):
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