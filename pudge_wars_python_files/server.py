import socket
import pickle
from threading import Thread, Lock

HOST = "26.140.237.173"  # Измените на ваш IP при необходимости
PORT = 5555

class GameServer:
    def __init__(self):
        self.clients = {}  # {conn: player_id}
        self.players = {}  # {player_id: player_data}
        self.next_player_id = 1
        self.lock = Lock()
        self.team_kills = {1: 0, 2: 0}
        self.game_over = False
        self.server = None  # Добавляем атрибут для серверного сокета
        print("[INIT] Сервер создан на 0.0.0.0:5555")

    def handle_client(self, conn, addr):
        player_id = None
        try:
            # Назначаем ID новому клиенту
            with self.lock:
                player_id = self.next_player_id
                self.next_player_id += 1
                self.clients[conn] = player_id
                print(f"[NEW] Клиент {addr} получил ID: {player_id}")
            
            # Отправляем ID клиенту
            init_data = {"your_id": player_id}
            conn.sendall(pickle.dumps(init_data))
            
            while True:
                try:
                    data = conn.recv(8192)
                    if not data:
                        print(f"[DISCONNECT] Клиент {addr} отключился (нет данных)")
                        break
                        
                    player_data = pickle.loads(data)
                    
                    # Проверяем на отключение
                    if isinstance(player_data, dict) and player_data.get("disconnect"):
                        print(f"[DISCONNECT] Клиент {addr} отправил сигнал отключения")
                        break
                    
                    with self.lock:
                        # Обработка киллов
                        
                        if "kill_event" in player_data:
                            killer_team = self.players[player_data["killer_id"]]["team"]
                            self.team_kills[killer_team] += 1
                            #player_data["kill_event"] = False
                        
                        if "game_over" in player_data:
                            print(f"[DEBUG] Получен сигнал о победе от клиента {addr}")
                            self.restart()

                        # Обновляем данные игрока
                        player_data["id"] = player_id
                        self.players[player_id] = player_data
                        
                        # Отправляем обновленное состояние всем клиентам
                        game_state = {
                            "players": list(self.players.values()),
                            "team_kills": self.team_kills,  # Добавляем счетчик в состояние
                            "game_over": self.game_over
                        }
                        state_data = pickle.dumps(game_state)
                        
                        disconnected = []
                        for client_conn, client_id in self.clients.items():
                            try:
                                client_conn.sendall(state_data)
                            except:
                                print(f"[ERROR] Не удалось отправить данные клиенту {client_id}")
                                disconnected.append(client_conn)
                        
                        # Удаляем отключившихся клиентов
                        for client_conn in disconnected:
                            self.remove_client(client_conn)
                                    
                except (pickle.UnpicklingError, EOFError) as e:
                    print(f"[ERROR] Ошибка данных от {addr}: {e}")
                    break
                    
        except Exception as e:
            print(f"[ERROR] Ошибка подключения {addr}: {e}")
            
        finally:
            # Удаляем отключившегося клиента
            if player_id is not None:
                self.remove_client(conn)
                print(f"[CLEANUP] Клиент {addr} (ID: {player_id}) удален")
                print(f"[STATUS] Активные клиенты: {self.clients}")
                print(f"[STATUS] Активные игроки: {self.players}")

    def remove_client(self, conn):
        """Удаляет клиента и его данные"""
        with self.lock:
            if conn in self.clients:
                player_id = self.clients[conn]
                # Удаляем данные игрока
                if player_id in self.players:
                    del self.players[player_id]
                # Удаляем связь сокет-ID
                del self.clients[conn]
                try:
                    conn.close()
                except:
                    pass
                print(f"[REMOVE] Удален клиент с ID {player_id}")

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("0.0.0.0", 5555))
        self.server.listen(6)
        print("[START] Сервер запущен...")
        
        while True:
            try:
                conn, addr = self.server.accept()
                print(f"[CONNECT] Новое подключение: {addr}")
                Thread(target=self.handle_client, args=(conn, addr)).start()
            except Exception as e:
                print(f"[ERROR] Ошибка при принятии подключения: {e}")
                
    def restart(self):
        print("[RESTART] Сервер перезапущен...")
        
        try:
            # Сразу запускаем bat-файл
            import subprocess
            import os
            subprocess.Popen(['server_restart.bat'], shell=True)
            os._exit(0)
            
        except Exception as e:
            print(f"[ERROR] Ошибка при запуске рестарта: {e}")
            os._exit(1)

if __name__ == "__main__":
    server = GameServer()
    server.start()