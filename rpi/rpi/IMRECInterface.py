from picamera import PiCamera
import cv2
import imagezmq
import socket
WIFI_IP = '192.168.20.25:5555'

class ImageRec:
    def __init__():
        self.sender = None
        self.reply = None
        self.camera = None
        self.rpi_name = None
        self.image = None
        self.ip_address = 'tcp://'+WIFI_IP
        self.obstacleLst =  None        
        print(f'[IMG REC] Setting up image recognition')

    def connect_IR(self):
        self.sender = imagezmq.ImageSender(connect_to=self.ip_address)
        self.socket = socket.gethostbyname()
        print(f'[IMG REC] Connected to Image Sender')
    
    def take_pic(self, obsLst):
        self.obstacleLst = obsLst
        self.camera = PiCamera(resolution=(640,640))
        self.rawCapture = PiRGBArray(self.camera)
        print(f'RPi name:\t',self.rpi_name)
        self.camera.capture(self.rawCapture, format = 'bgr')
        self.rawCapture.truncate(0)
        print(self.image)
        self.reply = self.sender.send_image(self.rpi_name, self.image)
        self.reply = str(self.reply.decode())
        print(f'Reply image:',self.reply)

        if self.reply =='n':
            print('Message recd. from RPi',self.reply)
        else:
            cls_id = self.reply
            if len(self.obstacleLst)>0:
                msg_to_send_AND = 'AND|OBS-'+str(self.obstacleLst[0])+'-'+str(cls_id)
                self.obstacleLst.pop(0)
    
        self.camera.stop_preview()
        self.camera.close()
