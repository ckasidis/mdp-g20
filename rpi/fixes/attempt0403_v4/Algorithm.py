import socket
import time
from env import *

class Algorithm:
    def __init__(self, ip=WIFI_IP, port=WIFI_PORT):
        self.ip = ip
        self.port = port
        print(f"Listening at IP: {self.ip}")
        self.connect = None
        self.client = None
        self.address = None
        self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connect.bind((self.ip, self.port))
        self.connect.listen(1)    
        
    def connect(self):
        while True:
            retry = False

            try:
                print('[ALGO-CONNECTION] Listening for ALG connections')

                if self.client is None:
                    self.client, self.address = self.connect.accept()
                    print('[ALGO-CONNECTION] Successfully connected with ALG: %s' % str(self.address))
                    retry = False

            except Exception as e:
                print('[ALGO-CONNECTION ERROR] %s' % str(e))

                if self.client is not None:
                    self.client.close()
                    self.client = None
                retry = True

            if not retry:
                break

            print('[ALGO-CONNECTION] Retrying connection with ALG')
            time.sleep(1)

    def disconnect(self):
        try:
            if self.connect is not None:
                self.connect.shutdown(socket.SHUT_RDWR)
                self.connect.close()
                self.connect = None
                print('[ALGO-DISCONNECT] Disconnecting Server Socket')

            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print('[ALGO-DISCONNECT] Disconnecting Client Socket')

        except Exception as e:
            print('[ALGO-DISCONNECT ERROR] %s' % str(e))    
            
    def read(self):
        try:
            msg = self.client.recv(ALGORITHM_SOCKET_BUFFER_SIZE)
            data = msg.decode()

            if len(data) > 0:
                return data

            return None

        except Exception as e:
            print('[ALGO-READ ERROR] %s' % str(e))
            raise e

    def write(self):
        try:
            self.client.send(message)

        except Exception as e:
            print('[ALGO-WRITE ERROR] %s' % str(e))
            raise e