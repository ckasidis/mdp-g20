import socket
import pickle
HEADERSIZE = 10


class Client:
    """
    Used as the client for RPI.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket()
    
    def connect(self):
        print(f"Attempting connection to ALGO at {self.host}:{self.port}")
        self.socket.connect((self.host, self.port))
        print("Connected to ALGO!")

    def receive(self):
        msg = self.socket.recv(1024)
        data = pickle.loads(msg)
        print(data)

    def send(self, data):
        msg = pickle.dumps(data)
        data = self.socket.send(msg)
    
    def close(self):
        print("Closing client socket.")
        self.socket.close()


if __name__ == '__main__':
    client = Client(socket.gethostbyname(socket.gethostname()), 3004)
    client.connect()
    obstacles = [[15, 185, -90, 0], [65, 125, 90, 1], [105, 75, 0, 2], [155, 165, 180, 3], [185, 95, 180, 4], [135, 25, 0, 5]]
    client.send(obstacles)
    client.receive()
    client.send('success')
    client.receive()
    client.send('success')
    client.receive()
    client.send('success')
    client.receive()
    client.send('success')
    client.receive()
    client.send('bullseye')
    client.receive()
    client.send('success')
    """
    for i in range(len(obstacles)):
        client.receive()
        client.send('success')
    """
