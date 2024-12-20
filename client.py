import socket
import pickle
import pygame
from config import *
from player import Player
import sys
SERVER_ADDRESS = "192.168.1.135"
SERVER_PORT = 5555


def serialize_player_data(player):
    """Создает словарь только с сериализуемыми данными игрока"""
    return {
        "id": id(player),
        "x": player.hitbox.x,
        "y": player.hitbox.y,
        "team": player.team,  # Добавляем team в сериализуемые данные
        "hook_active": player.hook.active,
        "hook_returning": player.hook.returning,
        "alive": player.alive,
        "hook_x": player.hook.rect.x if player.hook.active or player.hook.returning else None,
        "hook_y": player.hook.rect.y if player.hook.active or player.hook.returning else None
    }


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("dota 3")
    clock = pygame.time.Clock()

    # Подключение к серверу
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_ADDRESS, SERVER_PORT))
        sock.settimeout(0.1)
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу")
        return

    players = pygame.sprite.Group()
    local_player = Player(340, 200, players, team=1)
    bg_surf = pygame.image.load("data/images/background.jpg").convert()
    bg_surf = pygame.transform.scale(bg_surf, (WIDTH, HEIGHT))

    center_rect = pygame.Rect(714, 0, 400, HEIGHT)
    center_surf = pygame.Surface((400, HEIGHT))
    center_surf.set_alpha(0)

    left = right = up = down = show_hook_radius = False
    game_over = False
    winning_team = None

    while True:
        clock.tick(FPS)
        screen.blit(bg_surf, (0, 0))
        screen.blit(center_surf, center_rect)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sock.close()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == ord("w"):
                    up = True
                if event.key == ord("a"):
                    left = True
                if event.key == ord("s"):
                    down = True
                if event.key == ord("d"):
                    right = True
                if event.key == ord("q"):
                    if not local_player.hook.active and not local_player.hook.returning:
                        local_player.hook.launch(pygame.mouse.get_pos())
                if event.key == pygame.K_LALT:
                    show_hook_radius = True
            if event.type == pygame.KEYUP:
                if event.key == ord("w"):
                    up = False
                if event.key == ord("a"):
                    left = False
                if event.key == ord("s"):
                    down = False
                if event.key == ord("d"):
                    right = False
                if event.key == pygame.K_LALT:
                    show_hook_radius = False

        # Send player data to the server
        data_to_send = serialize_player_data(local_player)
        sock.sendall(pickle.dumps(data_to_send))

        # Receive game state from server
        try:
            server_data = sock.recv(4096)  # Receive up to 4096 bytes
            server_data = pickle.loads(server_data)  # Decode data with pickle
            
            if isinstance(server_data.get("players"), list):
                players.empty()
                for player_data in server_data["players"]:
                    if isinstance(player_data, dict):
                        new_player = Player(
                            player_data["x"], 
                            player_data["y"], 
                            players, 
                            player_data.get("team", 1)
                        )
                        new_player.alive = player_data.get("alive", True)
                        new_player.hook.active = player_data.get("hook_active", False)
                        new_player.hook.returning = player_data.get("hook_returning", False)
                        if player_data["id"] == id(local_player):
                            local_player = new_player
        except (socket.timeout, EOFError, pickle.UnpicklingError) as e:
            print(f"Error decoding server data: {e}")

        # Update local player
        local_player.move(left, right, up, down, center_rect, players)
        local_player.hook.move(players, {})

        if show_hook_radius:
            pygame.draw.circle(
                screen, (0, 255, 0), local_player.rect.center, HOOK_RADIUS, 1
            )

        # Draw players and hooks
        for player in players:
            if player.alive:
                screen.blit(player.image, player.rect)
            if player.hook.active or player.hook.returning:
                player.hook.draw_chain(screen)
                screen.blit(player.hook.image, player.hook.rect)

        pygame.display.update()

if __name__ == "__main__":
    main()