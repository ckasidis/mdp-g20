# # ==========================================================
# # Main script For Week 9 Task 
# # Managing the communication between RPi and STM, RPi and Android
# # ===============================================================

import time

import imagezmq
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray

import base64
import os
import glob
import socket

img_directory = "/home/pi/rpi/picamera_images/"
image_processing_server_url = "tcp://192.168.20.25:5555"
image_count = 0 # keep track of the images detected

# Take photo
def takePic():
    try:
            rawCapture = PiRGBArray(camera)
            camera.capture(rawCapture, format = 'bgr')
            image = rawCapture.array
            print("[MAIN] Image successfully taken.")
            #cv2.imwrite("test.jpg", image)
    except Exception as e:
            print(f"[ERROR] Unable to take pic: {str(e)}")
    return image

# Processing image - send it to the image processing server
def process_image(x, image):
    # Initialise the ImageSender object with the socket address of the server
    image_sender = imagezmq.ImageSender(connect_to = image_processing_server_url)
    global image_count, image_id_lst
    try:
        rpi_name = socket.gethostname() # send RPi hostname with each image
        print("[MAIN] Sending image to image processing server...")
        reply = image_sender.send_image(rpi_name, image)
        reply = reply.decode('utf-8')

        if reply == "39":  # left arrow
            print("[MAIN] Left Arrow") 
            result = f"picture {x}: left"

        elif reply == "38": #right arrow
            print("[MAIN] Right Arrow") 
            result = f"picture {x}: right"

        else:
            result = f"picture {x}: nothing"

        image_sender.close()
        return result

    except Exception as e:
        print(f"[Error] Image processing failed: {str(e)}")


import serial 

ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/ttyUSB0'
# ser.port = '/dev/cu.usbserial-0002'
print(ser.open())
init = ['US025'] # move until 25cm before 1st obstacle
case_l = [
    # scan 1 = left
    'FL057', 'FR057', 'FW020',
    # move to 2nd obs
    'US230', # move until 30cm before 2nd obstacle
    'FR020',
]

case_r = [
    # scan 1 = right
    'FR057', 'FL057', 'FW020',
    # move to 2nd obs
    'US030', # move until 30cm before 2nd obstacle and save d to buff 0
    'FL020',
]

case_ll = [
    # scan 2 = left
    'BR020', 'FL067', 'FR067', 'FW030', 'FR090', 'FW067', 'FR090',
    'RT099', # d + 99
    'FR090', 'FW010', 'FL090',
    # back to base
    'US120' # move until 20cm before parking wall
]

case_lr = [
    # scan 2 = right
    'FR070', 'FW035', 'FL090', 'FW030', 'FL090', 'FW067', 'FL090', 
    'RT099', # d + 99
    'FL090', 'FW010', 'FR090',
    # back to base
    'US120' # move until 20cm before parking wall
]

case_rr = [
    # scan 2 = left
    'BL020', 'FR067', 'FL067', 'FW030', 'FL090', 'FW067', 'FL090',
    'RT099', # d + 99
    'FL090', 'FW010', 'FR090',
    # back to base
    'US120' # move until 20cm before parking wall
]

case_rl = [
    # scan 2 = right
    'FL070', 'FW035', 'FR090', 'FW030', 'FR090', 'FW067', 'FR090', 
    'RT099', # d + 99
    'FR090', 'FW010', 'FL090',
    # back to base
    'US120' # move until 20cm before parking wall
]

# instr_list = init + case_l + case_ll
# instr_list = init + case_l + case_lr
# instr_list = init + case_r + case_rr
# instr_list = init + case_r + case_rl
i1,i2 = 'left','left'

for instr in instr_list:
    if instr=="RPI|TOCAM":
        image = takePic()
        result = process_image(1, image)
        if "right" in result:
            for i in case_r:
                ser.write(i.encode())
    print(instr)
    ser.write(instr.encode())
    while True:
        raw_dat = ser.read(1)
        dat = raw_dat.strip().decode()
        print(raw_dat)
        if dat == 'R':
            break
print("done")






