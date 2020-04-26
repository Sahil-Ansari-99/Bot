import socket
import base64


class Client:
    def __init__(self, name):
        self.name = name
        self.HEADER = 64
        self.PORT = 8080
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.COMPRESS_FORMAT = '!COMPRESS'
        self.SERVER = '127.0.1.1'
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)

    def start(self):
        connected = True
        while connected:
            msg = input('Enter Message ')
            if msg == self.DISCONNECT_MESSAGE:
                connected = False
            if msg == 'pic':
                self.send_pic(True, False)
            if msg == self.COMPRESS_FORMAT:
                self.send_pic(True, True)
            else:
                self.send(msg)

    def send(self, msg):
        message = msg.encode(self.FORMAT)
        msg_length = len(msg)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        return_msg = self.client.recv(2048).decode(self.FORMAT)
        print(return_msg)
        if return_msg.startswith('GOT SIZE'):
            self.send_pic(True, False)

    def send_pic(self, send, compress):
        pic = 'dog.jpg'
        pic_file = open(pic, 'rb')
        bytes = pic_file.read()
        pic_size = len(bytes)
        msg = f'P!C {pic_size}'
        if not send:
            self.send(msg)
        else:
            pic_base64 = base64.b64encode(bytes)
            pic_base64 = str(pic_base64)
            if compress:
                pic_base64 = '!COMPRESS' + pic_base64
            else:
                pic_base64 = '$P!C' + pic_base64
            self.send(pic_base64)


client = Client('Test')
client.start()
