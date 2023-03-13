# ==========================================================
# Main script For Week 9 Task 
# Managing the communication between RPi and STM, RPi and Android
# ===============================================================

import time

from STM32 import STM32
from Android import Android

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
def process_image(image):
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

def readSTM(command):
    data = ""
    while True:
        data = interfaces[STM].read()
        print(f"DATA FROM STM: {data}")
        if data:
            return

# ===============================================================================================


if __name__ == '__main__':

    print("[MAIN] Initialising Multiprocessing Communication ...")

    interfaces = []
    interfaces.append(STM32())

    STM = 0

    for interface in interfaces:
        interface.connect() # connect STM first, then Android

    print("[MAIN] Multiprocess communication started.")

    # Set up PiCamera
    print("[MAIN] Setting up PiCamera...")
    camera = PiCamera()
    print("[MAIN] PiCamera ready.")

    # Initialise variables
    p_s = ['US025']

    p_l = [
        # scan 1 = left
        'FL057', 'FR057', 'FW020',
        # move to 2nd obs
        'US230', # move until 30cm before 2nd obstacle
        'FR020',
    ]

    p_r = [
        # scan 1 = right
        'FR057', 'FL057', 'FW020',
        # move to 2nd obs
        'US030', # move until 30cm before 2nd obstacle and save d to buff 0
        'FL020',
    ]


    p_ll = [
        # scan 2 = left
        'BR020', 'FL067', 'FR067', 'FW030', 'FR090', 'FW067', 'FR090',
        'RT099', # d + 99
        'FR090', 'FW010', 'FL090',
        # back to base
        'US120' # move until 20cm before parking wall
    ]

    p_lr = [
        # scan 2 = right
        'FR070', 'FW035', 'FL090', 'FW030', 'FL090', 'FW067', 'FL090', 
        'RT099', # d + 99
        'FL090', 'FW010', 'FR090',
        # back to base
        'US120' # move until 20cm before parking wall
    ]

    p_rr = [
        # scan 2 = left
        'BL020', 'FR067', 'FL067', 'FW030', 'FL090', 'FW067', 'FL090',
        'RT099', # d + 99
        'FL090', 'FW010', 'FR090',
        # back to base
        'US120' # move until 20cm before parking wall
    ]

    p_rl = [
        # scan 2 = right
        'FL070', 'FW035', 'FR090', 'FW030', 'FR090', 'FW067', 'FR090', 
        'RT099', # d + 99
        'FR090', 'FW010', 'FL090',
        # back to base
        'US120' # move until 20cm before parking wall
    ]

    r1 = "left"
    r2 = "left"

    print("[MAIN]: Heading to 1st obstacle.")

    try: 
        for i in p_s:
            content = i
            interfaces[STM].write(content)
            readSTM(content)

        # Taking pic for 1st obstacle
        image = takePic()
        result_msg = process_image(image)
        print(result_msg)
        print("[MAIN]: Heading to 2nd obstacle.")
        if "right" in result_msg:
            r1 = "right"
            for i in p_r:
                content = i
                interfaces[STM].write(content)
                readSTM(content)
        else:
            for i in p_l:
                content = i
                interfaces[STM].write(content)
                readSTM(content)
        
        #Taking pic for 2nd obstacle
        image = takePic()
        result_msg = process_image(image)
        print(result_msg)
        print("[MAIN]: Heading back to carpark.")
        if "right" in result_msg:
            if r1 == "right":
                for i in p_rr:
                    content = i
                    interfaces[STM].write(content)
                    readSTM(content)
            else:
                for i in p_lr:
                    content = i
                    interfaces[STM].write(content)
                    readSTM(content)
        else:
            if r1 == "right":
                for i in p_rl:
                    content = i
                    interfaces[STM].write(content)
                    readSTM(content)
            else:
                for i in p_ll:
                    content = i
                    interfaces[STM].write(content)
                    readSTM(content)
        # image = takePic()
        # result_msg = process_image(image)
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        for i in interfaces:
            i.disconnect()
        camera.close()

    finally:
        for i in interfaces:
            i.disconnect()
        camera.close()
        print("[MAIN] Camera closed.")








