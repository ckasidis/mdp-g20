import pickle
import socket
import time

WIFI_IP = "192.168.13.26"
WIFI_PORT = 3004
ALGORITHM_SOCKET_BUFFER_SIZE = 1024
from colorama import *

init(autoreset=True)


class Algo:
    def __init__(self, host=WIFI_IP, port=WIFI_PORT):
        self.host = host
        self.port = port
        self.socket = socket.socket()

        """ self.connect = None
        self.client = None
        self.address = None

        self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connect.bind((self.ip, self.port))
        self.connect.listen(1) """

    def connect_ALG(self):
        while True:
            retry = False

            try:
                print(Fore.LIGHTYELLOW_EX + f'[ALG-CONN] Listening for ALG connection at {self.host}:{self.port}')
                self.socket.connect((self.host, self.port))
                print(Fore.GREEN + "[ALG-CONN] Successful")
                retry = False
            except Exception as e:
                print(Fore.RED + '[ALG-CONN ERROR] %s' % str(e))

            if not retry:
                break

            print(Fore.LIGHTYELLOW_EX + '[ALG-CONN] Retrying connection with ALG...')
            time.sleep(1)

    def disconnect_all(self):
        try:
            if self.connect is not None:
                self.connect.shutdown(socket.SHUT_RDWR)
                self.connect.close()
                self.connect = None
                print(Fore.LIGHTWHITE_EX + '[ALG-DCONN] Disconnecting Server Socket')

            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print(Fore.LIGHTWHITE_EX + '[ALG-DCONN] Disconnecting Client Socket')

        except Exception as e:
            print(Fore.RED + '[ALG-DCONN ERROR] %s' % str(e))

    def disconnect_ALG(self):
        try:
            self.socket.close()
            print(Fore.LIGHTWHITE_EX + '[ALG-DCONN] Disconnecting Client Socket')

        except Exception as e:
            print(Fore.RED + '[ALG-DCONN ERROR] %s' % str(e))

    def read_from_ALG(self):
        try:
            msg = self.socket.recv(ALGORITHM_SOCKET_BUFFER_SIZE)
            data = msg.decode()
            print(data)

            if len(data) > 0:
                return data

            return None

        except Exception as e:
            print(Fore.RED + '[ALG-READ ERROR] %s' % str(e))
            raise e

    def write_to_ALG(self, msg):
        try:
            self.socket.send(msg)
        except Exception as e:
            print(Fore.RED + '[ALG-WRITE ERROR] %s' % str(e))
            raise e


if __name__ == '__main__':
    client = Algo()
    #ser.__init__()
    client.connect_ALG()
    time.sleep(3)
    print('Connection established')
    obstacles = [[15, 185, -90, 0], [65, 125, 90, 1], [105, 75, 0, 2], [155, 165, 180, 3], [185, 95, 180, 4], [135, 25, 0, 5]] 
    while True: 
        try:            
            client.write_to_ALG(obstacles)
            msg = client.read_from_ALG()
            client.write_to_ALG('success')
        except KeyboardInterrupt:
            print('Communication interrupted')
            client.disconnect_ALG()
            break
