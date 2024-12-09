import socket
from threading import Thread

ADDR = ('localhost', 8800) # server address
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
    
if __name__ == "__main__":
    server = Server(ADDR, MAX_PLAYERS)