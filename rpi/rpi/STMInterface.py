import serial
import time
from colorama import *

# import signal

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

init(autoreset=True)

class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

import time
import signal

class TimeoutException(Exception):   # Custom exception class
    pass


def break_after(seconds=2):
    def timeout_handler(signum, frame):   # Custom signal handler
        raise TimeoutException
    def function(function):
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                res = function(*args, **kwargs)
                signal.alarm(0)      # Clear alarm
                return res
            except TimeoutException:
                print (f'Oops, timeout: %s sec reached.' % seconds, function.__name__, args, kwargs)
            return
        return wrapper
    return function

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
            print("trying again")
            time.sleep(0.5)
        
            #raise e

    @break_after(5)
    def read_rawdat_function(self):
        raw_dat = self.STM_connection.read(1)
        print("raw_dat: " + str(raw_dat))
        dat = raw_dat.strip().decode()
        if dat == 'R':
            # print("received R reply from STM")
            # break
            return True
        return Falses
    
    # @break_after(5)
    def write_to_STM(self, message):
        try:
            if self.STM_connection is None:
                print('[STM-CONN] STM is not connected. Trying to connect...')
                self.connect_STM()
            print('In STM: write to STM method: before Transmitted to STM:')
            print('\t %s' % message)
            st = time.time()
            self.STM_connection.write(message.encode())
            print(message +" sent")
            print('In STM: write to STM method: after Transmitted to STM')
            # signal.signal(signal.SIGALRM, timeout_handler)
            while True:
                try:
                    # Change the behavior of SIGALRM
                    # signal.alarm(5)
                    # try:
                        # if self.STM_connection is None:
                        #     print('[STM-CONN] STM is not connected. Trying to connect...')
                        #     self.connect_STM()
                    if read_rawdat_function():
                        break
                        # raw_dat = self.STM_connection.read(1)
                        # print("raw_dat: " + str(raw_dat))
                        # dat = raw_dat.strip().decode()
                        # if dat == 'R':
                        #     print("received R reply from STM")
                        #     break
                    # except TimeoutException:
                    #     break # continue the for loop if function A takes more than 5 second
                    # else:
                    #     # Reset the alarm
                    #     signal.alarm(0)
                except Exception as e:
                    print("error caught in write_to_STM....trying again")
                    time.sleep(0.5)
                    continue
        except Exception as e:
            print('[STM-WRITE Error] write_to_STM() function %s' % str(e))
            #raise e

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
