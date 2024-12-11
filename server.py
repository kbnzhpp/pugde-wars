import socket
from threading import Thread

ADDR = ('127.0.0.1', 8800) # server address
MAX_PLAYERS = 6 # maximum connections

class Server:
    def __init__(self, address, clients):
        self.sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(address) # starting server

        self.max_players = clients
        self.players_connected = []

        self.sock.listen(self.max_players) # maximum players can connect

    def listen(self):
        while True:
            if not len(self.players_connected) >= self.max_players: # проверяем не превышен ли лимит
                conn, addr = self.sock.accept()

                print("New connection", addr)

                Thread(target=self.handle_client, args=(conn,)).start()
            conn, addr = self.sock.accept()
    
    def handle_client(self, conn):
        # Настраиваем стандартные данные для игрока
        self.player = {
            "id": len(self.players),
            "x": 400,
            "y": 300
        }
        self.players_connected.append(self.player) # добавляем его в массив игроков

        while True:
            try:
                data = conn.recv(1024) # ждем запросов от клиента

                if not data: # если запросы перестали поступать, то отключаем игрока от сервера
                    print("Disconnect")
                    break

                # загружаем данные в json формате
                data = json.loads(data.decode('utf-8'))

                # запрос на получение игроков на сервере
                if data["request"] == "get_players":
                    conn.sendall(bytes(json.dumps({
                        "response": self.players
                    }), 'UTF-8'))

                # движение
                if data["request"] == "move":

                    if data["move"] == "left":
                        self.player["x"] -= 1
                    if data["move"] == "right":
                        self.player["x"] += 1
                    if data["move"] == "up":
                        self.player["y"] -= 1
                    if data["move"] == "down":
                        self.player["y"] += 1
            except Exception as e:
                print(e)
                break

        self.players.remove(self.player) # если вышел или выкинуло с сервера - удалить персонажа
        
if __name__ == "__main__":
    server = Server(ADDR, MAX_PLAYERS)