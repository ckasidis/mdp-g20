import socket
import time
import pickle
import json
import numpy as np

WIFI_IP = "192.168.20.1"
WIFI_PORT = 3004
ALGORITHM_SOCKET_BUFFER_SIZE = 9

# To be there on RPi.

class Algo:
    def __init__(self, ip=WIFI_IP, port=WIFI_PORT):
        ''' Setup the class with basic parameters and attributes'''
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

    def connect_ALG(self):
        ''' Establish a socket connection'''
        while True:
            retry = False

            try:
                print('[ALG-CONN] Listening for ALG connections...')

                if self.client is None:
                    self.client, self.address = self.connect.accept()
                    print('[ALG-CONN] Successfully connected with ALG: %s' % str(self.address))
                    retry = False

            except Exception as e:
                print('[ALG-CONN ERROR] %s' % str(e))

                if self.client is not None:
                    self.client.close()
                    self.client = None
                retry = True

            if not retry:
                break

            print('[ALG-CONN] Retrying connection with ALG...')
            time.sleep(1)

    def disconnect_all(self):
        try:
            if self.connect is not None:
                self.connect.shutdown(socket.SHUT_RDWR)
                self.connect.close()
                self.connect = None
                print('[ALG-DCONN] Disconnecting Server Socket')

            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print('[ALG-DCONN] Disconnecting Client Socket')

        except Exception as e:
            print('[ALG-DCONN ERROR] %s' % str(e))

    def disconnect_ALG(self):
        try:
            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print('[ALG-DCONN] Disconnecting Client Socket')

        except Exception as e:
            print('[ALG-DCONN ERROR] %s' % str(e))

    def read_from_ALG(self):
        try:
            # msg = self.client.recv()
            msg = self.client.recv(ALGORITHM_SOCKET_BUFFER_SIZE)
            data = msg.decode()
            # Converting the string to an array
            # arr = np.array(data.split(','), dtype=np.int)

            # print("Received command:", data)

            if len(data) > 0:
                return data

            return None

        except Exception as e:
            print('[ALG-READ ERROR] %s' % str(e))
            raise e

    def write_to_ALG(self, message):
        try:
            self.client.send(message)

        except Exception as e:
            print('[ALG-WRITE ERROR] %s' % str(e))
            raise e


if __name__ == '__main__':
    ser = Algo()
    ser.connect_ALG()
    time.sleep(3)
    print('Connection established')
    count = 1
    while True: 
        try:            
            if(count == 1):
                obstacles = "ALGO|[[2,8,S], [6,12,N], [8,5,E], [15,16,S], [16,1,W]]"
                data = obstacles.encode()
                ser.write_to_ALG(data)
                count+=1
            else:
                writeMsg = "ALG|CMPLT"
                ser.write_to_ALG(writeMsg.encode())
            
            jsonMsg = ser.read_from_ALG()
            # msg = json.loads(jsonMsg)
            if jsonMsg is None:
                ser.disconnect_ALG()
                ser.disconnect_all()
                break

            print(f"Command received from PC : {jsonMsg}")

            


        except KeyboardInterrupt:
            print('Communication interrupted')
            ser.disconnect_ALG()
            ser.disconnect_all()
            break