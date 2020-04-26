import socket
import threading
from bot import Bot


class Server:
    def __init__(self):
        self.clients = []
        self.HEADER = 64
        self.PORT = 8080
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.ADDR)
        self.connected_clients = []

    def start(self):
        self.server.listen()
        print("LISTENING ON ", self.SERVER)
        while True:
            try:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
                print("Connections ", threading.activeCount() - 1)
                print(self.connected_clients)
            except KeyboardInterrupt:
                print("Keyboard Interrupt")
                self.close()
                exit(0)

    def handle_client(self, conn, addr):
        self.connected_clients.append(addr)
        connected = True
        bot = Bot()
        while connected:
            msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)
                if msg == self.DISCONNECT_MESSAGE:
                    connected = False
                print(addr, msg)
                ret = bot.process_message(msg)
                conn.send(ret.encode(self.FORMAT))
        self.connected_clients.remove(addr)
        conn.close()

    def close(self):
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()


if __name__ == '__main__':
    server = Server()
    server.start()
