import serial
import time
from colorama import *

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

init(autoreset=True)

class STM:
    def __init__(self):
        self.port = SERIAL_PORT
        self.baud_rate = BAUD_RATE
        self.STM_connection = None

    def connect_STM(self):
        print('[STM-CONN] Waiting for serial connection...')
        while True:
            retry = False

            try:
                self.STM_connection = serial.Serial(self.port, self.baud_rate)

                if self.STM_connection is not None:
                    print('[STM-CONN] Successfully connected with STM:')
                    retry = False

            except Exception as e:
                print('[STM-CONN ERROR] %s' % str(e))
                retry = True

            if not retry:
                break

            print('[STM-CONN] Retrying connection with STM...')
            time.sleep(1)

    def disconnect_STM(self):
        try:
            if self.STM_connection is not None:
                self.STM_connection.close()
                self.STM_connection = None
                print('[STM-DCONN ERROR] Successfully closed connection')

        except Exception as e:
            print('[STM-DCONN ERROR] %s' % str(e))

    def read_from_STM(self):
        print("Reading")
        try:
            self.STM_connection.flush()
            get_message = self.STM_connection.read(9)
            print(get_message)
#            get_message = get_message.decode()
#            print("STM is sending this:" + get_message)
            

            if len(get_message) > 0:
                return get_message

            return None

        except Exception as e:
            print('[STM-READ ERROR] %s' % str(e))
            raise e

    def write_to_STM(self, message):
        try:
            if self.STM_connection is None:
                print('[STM-CONN] STM is not connected. Trying to connect...')
                self.connect_STM()

            print('In STM: write to STM method: before Transmitted to STM:')
            print('\t %s' % message)
            self.STM_connection.write(message)
            print(message.decode()+" sent")
            print('In STM: write to STM method: after Transmitted to STM')

        except Exception as e:
            print('[STM-WRITE Error] %s' % str(e))
            raise e


if __name__ == '__main__':
    ser = STM()
#    ser.__init__()
    ser.connect_STM()
    while True:
        try:
            msg = input("Enter message to send to STM: ")
            msg = str(msg).encode()
            ser.write_to_STM(msg)
#            time.sleep(5)
            ser.read_from_STM()
        except KeyboardInterrupt:
            print('Serial Communication Interrupted.')
            ser.disconnect_STM()
            break   
