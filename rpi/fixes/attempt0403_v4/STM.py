import serial
import time
from env import *

class STM:
    def __init__(self):
        self.port = SERIAL_PORT
        self.baud_rate = BAUD_RATE
        self.STM_connection = None
    
    def connect(self):
        print('[STM-CONNECTION] Waiting for serial connection...')
        while True:
            retry = False

            try:
                self.STM_connection = serial.Serial(self.port, self.baud_rate)

                if self.STM_connection is not None:
                    print('[STM-CONNECTION] Successfully connected with STM:')
                    retry = False

            except Exception as e:
                print('[STM-CONNECTION ERROR] %s' % str(e))
                retry = True

            if not retry:
                break

            print('[STM-CONNECTION] Retrying connection with STM...')
            time.sleep(1)
    
    def disconnect(self):
        try:
            if self.STM_connection is not None:
                self.STM_connection.close()
                self.STM_connection = None
                print('[STM-DISCONNECT ERROR] Successfully closed connection')

        except Exception as e:
            print('[STM-DISCONNECT ERROR] %s' % str(e))

    def read(self):
        try:
            self.STM_connection.flush()
            get_message = self.STM_connection.read(9)
            print(get_message)
            if len(get_message) > 0:
                return get_message
            else:
                return None

        except Exception as e:
            print('[STM-READ ERROR] %s' % str(e))
            raise e
    
    def write(self, message):
        try:
            if self.STM_connection is None:
                print('[STM-CONNECTION] STM is not connected. Trying to connect...')
                self.connect_STM()
            print('\t %s' % message)
            print('[STM-WRTIE] before transmitted to STM:')
            self.STM_connection.write(message)
            print(message.decode()+" sent")
            print('[STM-WRTIE] after transmitted to STM')

        except Exception as e:
            print('[STM-WRITE Error] %s' % str(e))
            raise e