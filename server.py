import socket
import pickle
from threading import Thread, Lock

HOST = "192.168.1.135"  # Измените на ваш IP при необходимости
PORT = 5555

class GameServer:
    def __init__(self):
        self.clients = []
        self.players = {}
        self.lock = Lock()
        self.next_player_id = 1
        print("Сервер инициализирован")
        
    def handle_client(self, conn, addr):
        player_id = self.next_player_id
        self.next_player_id += 1
        print(f"Новый игрок подключился. ID: {player_id}")
        
        try:
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                        
                    player_data = pickle.loads(data)
                    print(f"Получены данные от игрока {player_id}: {player_data}")
                    
                    with self.lock:
                        self.players[player_data["id"]] = player_data
                        game_state = {
                            "players": list(self.players.values())
                        }
                        print(f"Отправка состояния игры: {game_state}")
                        self.broadcast(game_state)
                        
                except (EOFError, pickle.UnpicklingError) as e:
                    print(f"Ошибка обработки данных от {addr}: {e}")
                    break
                    
        finally:
            print(f"Игрок {player_id} отключился")
            conn.close()
            self.clients.remove(conn)
            with self.lock:
                if player_id in self.players:
                    del self.players[player_id]

    def broadcast(self, data):
        """Отправка данных всем подключенным клиентам"""
        serialized_data = pickle.dumps(data)
        for client in self.clients[:]:
            try:
                client.sendall(serialized_data)
            except:
                self.clients.remove(client)

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Сервер запущен на {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            print(f"Новое подключение: {addr}")
            self.clients.append(conn)
            Thread(target=self.handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    GameServer().start()