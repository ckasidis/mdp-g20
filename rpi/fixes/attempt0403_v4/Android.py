import socket
from bluetooth import *
import os
from env import *

class Android:
    def __init__(self):
        self.server = None
        self.client = None
        os.system('sudo hciconfig hci0 piscan')
        self.server = BluetoothSocket(RFCOMM)
        self.server.bind(("",PORT_ANY))
        self.server.listen(PORT_ANY)
        self.port = self.server.getsockname()[1]

        advertise_service(
            self.server, 
            'MDP-Team-20',
            service_id=UUID,
            service_classes=[UUID, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
        )

        print('[BT] Waiting for BT connection on RFCOMM channel %d' % self.port)

    def connect(self):
        # CONNECT TO ANDROID 
        while True:
            retry = False

            try:
                print('[AND-CONN] Connecting to ANDROID')

                if self.client is None:
                    self.client, address = self.server.accept()
                    print('[ANDROID-CONNECTION] Successful connected with AND: %s ' % str(address))
                    retry = False

            except Exception as e:
                print('[ANDROID-CONNECTION ERROR] %s' % str(e))

                if self.client is not None:
                    self.client.close()
                    self.client = None

                retry = True

            if not retry:
                break

            print('[ANDROID-CONNECTION] Retrying connection with ANDROID')


    def disconnect(self):
        # DISCONNECT CLIENT AND SERVER
        try:
            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print('[AND-DCONN] Disconnecting Client Socket')

            if self.server is not None:
                self.server.shutdown(socket.SHUT_RDWR)
                self.server.close()
                self.server = None
                print('[AND-DISCONNECT] Disconnecting Server Socket')

        except Exception as e:
            print('[ANDROID-DISCONNECT ERROR] %s' % str(e))


    def read(self):
        try:
            msg = self.client.recv(ANDROID_SOCKET_BUFFER_SIZE).strip()
            print(msg)
            if msg is None:
                return None
            if len(msg) > 0:
                return msg

            return None

        except BluetoothError as e:
            print('[ANDROID-READ ERROR] %s' % str(e))
            raise e

    def write(self, message):
        try:
            self.client.send(message)

        except BluetoothError as e:
            print('[ANDROID-WRITE ERROR] %s' % str(e))
            raise e