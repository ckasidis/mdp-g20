""" import socket
from bluetooth import *

UUID = "00001101-0000-1000-8000-00805F9B34FB"
ANDROID_SOCKET_BUFFER_SIZE = 2048

class AndroidInterface:
    def __init__(self):
        self.client = None
        self.server = BluetoothSocket(RFCOMM)
        self.server.bind("", PORT_ANY)
        self.server.listen(1)
        self.port = self.server.getsockname()[1]

        advertise_service(
            self.server, "MDP_Team13",
            service_id=UUID,
            service_classes=[UUID, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
        )

        print('[BT] Waiting for BT connection on RFCOMM channel %d' % self.port)
    
    def connect(self):
        if self.client is None:
            self.client, client_info = self.server.accept()
            print("Accepted connection from ",client_info)

    def read(self):
        try:
            while True:
                req = self.client.recv(2048).strip()
                if len(req) == 0:
                    break
                print(req)
        except:
            pass
          
androidServer = AndroidInterface()
androidServer.connect()

while True:
    androidServer.read() """

