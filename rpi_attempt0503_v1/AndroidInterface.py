import socket
from bluetooth import *
import os

UUID = "00001101-0000-1000-8000-00805F9B34FB"
ANDROID_SOCKET_BUFFER_SIZE = 2048

#init(autoreset=True)

class Android:
    def __init__(self):
        
        self.server = None
        self.client = None

        os.system('sudo hciconfig hci0 piscan')
        self.server = BluetoothSocket(RFCOMM)
#        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#        self.server.close()
        self.server.bind(("",PORT_ANY))
        self.server.listen(PORT_ANY)
        self.port = self.server.getsockname()[1]

        advertise_service(
            self.server, 'MDP-Team31',
            service_id=UUID,
            service_classes=[UUID, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
        )
        print('[BT] Waiting for BT connection on RFCOMM channel %d' % self.port)

    def connect_AND(self):
        while True:
            retry = False

            try:
                print('[AND-CONN] Connecting to AND...')

                if self.client is None:
                    self.client, address = self.server.accept()
                    print('[AND-CONN] Successful connected with AND: %s ' % str(address))
                    retry = False

            except Exception as e:
                print('[AND-CONN ERROR] %s' % str(e))

                if self.client is not None:
                    self.client.close()
                    self.client = None

                retry = True

            if not retry:
                break

            print('[AND-CONN] Retrying connection with AND...')

    def disconnect_AND(self):
        try:
            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print('[AND-DCONN] Disconnecting Client Socket')

        except Exception as e:
            print('[AND-DCONN ERROR] %s' % str(e))

    def disconnect_all(self):
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
                print('[AND-DCONN] Disconnecting Server Socket')

        except Exception as e:
            print('[AND-DCONN ERROR] %s' % str(e))

    def read_from_AND(self):
        try:
            msg = self.client.recv(ANDROID_SOCKET_BUFFER_SIZE).strip()
            print(msg)
            if msg is None:
                return None

            if len(msg) > 0:
                return msg

            return None

        except BluetoothError as e:
            print('[AND-READ ERROR] %s' % str(e))
            raise e

    def write_to_AND(self, message):
        try:
            self.client.send(message)

        except BluetoothError as e:
            print('[AND-WRITE ERROR] %s' % str(e))
            raise e


if __name__ == '__main__':
    ser = Android()
#    ser.__init__()
    ser.connect_AND()
    while True:
        try:
            print('In loop')
            msg = ser.read_from_AND()
#           print(msg)
#            writemsg = str(input('insert msg')+ ' from rpi' )
#            ser.write_to_AND(writemsg)
        except KeyboardInterrupt:
            print('AND communication interrupted.')
            ser.disconnect_AND()
            break

