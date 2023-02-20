import serial
from colorama import *
from imutils.video import VideoStream
from picamera import PiCamera
from picamera.array import PiRGBArray
import imagezmq
import argparse
import socket
import time

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

init(autoreset=True)

class STM:
    def __init__(self):
        self.port = SERIAL_PORT
        self.baud_rate = BAUD_RATE
        self.STM_connection = None
        self.IMG_sender = None
        self.rpiName = None

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
        
    def write_to_STM_test(message):
        try:

            print('In STM: write to STM method: before Transmitted to STM:')
            print('\t %s' % message)
            print(message.decode()+" sent")
            print('In STM: write to STM method: after Transmitted to STM')

        except Exception as e:
            print('[STM-WRITE Error] %s' % str(e))
            raise e

    def connect_to_imgsv(self):

            
        self.IMG_sender = imagezmq.ImageSender(connect_to='tcp://192.168.20.25:5555')
        self.rpiName = socket.gethostname()

        if self.IMG_sender is not None:
            print(self.rpiName,"connected to imgserver")
                    

    def take_image(self):
        try:
            if self.IMG_sender is None:
                print(' IMG is not connected. Trying to connect...')
                
                self.IMG_sender = imagezmq.ImageSender(connect_to='tcp://192.168.20.25:5555')
                self.rpiName = socket.gethostname()

            camera = PiCamera(resolution=(640, 640))
            rawCapture = PiRGBArray(camera)
            print("printing rawCapture: " + str(rawCapture))
            camera.capture(rawCapture, format="rgb")
            image = rawCapture.array
            print("printing image: " + str(image))
            rawCapture.truncate(0)
            print("trying to send image")
            print("rpiName: " + str(self.rpiName))
            reply = self.IMG_sender.send_image(self.rpiName, image)
            print("Receiving reply")
            reply = str(reply.decode())
            camera.close()
            return reply

        except Exception as e:
            print('[take_image Error] %s' % str(e))
            raise e
        
        


if __name__ == '__main__':
    img = STM()
#    ser.__init__()
    img.connect_STM()
    ser = serial.Serial()
    
    
    print("entering loop")
    while True:
        reply = img.take_image()
        print("Img server reply: " + reply)
        if reply != "0": 
            img.disconnect_STM() 
            break
        
        instr_list = [
            'FW025',
            'FL090',
        ]
        
        for instr in instr_list:
            img.write_to_STM(instr.encode())
            while True:
                bytestoRead = ser.inWaiting()
                raw_dat=ser.read(1)
                dat = raw_dat.strip().decode()
                if dat == 'R':
                    break
