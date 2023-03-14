import os
import socket

import cv2
import imagezmq
import serial
from picamera import PiCamera
from picamera.array import PiRGBArray

img_directory = "/home/pi/mdp-g20/fixrpi/picamera_images/"
image_processing_server_url = "tcp://192.168.20.25:5555"
image_count = 0  # keep track of the images detected

def move_stm(instr_list):
    """
    Move STM32 using a list of instructions

    Args:
        instr_list: list of instructions to be sent to STM32 (list)
    """
    
    for instr in instr_list:
        stm.write(instr.encode())
        while True:
            raw_dat = stm.read(1)
            dat = raw_dat.strip().decode()
            if dat == "R":
                return

def take_pic():
    """
    Take a picture using PiCamera

    Returns:
        Image: frame captured by PiCamera (cv2.Image)
    """
    
    try:
        rawCapture = PiRGBArray(camera)
        camera.capture(rawCapture, format="bgr")
        image = rawCapture.array
        print("[TAKE PIC] Image successfully taken.")

    except Exception as e:
        print(f"[TAKE PIC][ERROR] Unable to take pic: {str(e)}")
        
    return image

def process_image(image):
    """
    Process the image using the image processing server
    Run the YOLOv5 model on the image and return the class ID

    Args:
        image: frame captured by PiCamera (cv2.Image)

    Returns:
        class_id: Class ID of the object detected in the image (str)
    """
    
    image_sender = imagezmq.ImageSender(connect_to = image_processing_server_url)
    global image_count, image_id_lst
    try:
        rpi_name = socket.gethostname() # send RPi hostname with each image
        reply = image_sender.send_image(rpi_name, image)
        reply = reply.decode('utf-8')

        if reply == "n":  # no image detected
            class_id = f"n"

        elif reply == "00" or reply=='0': # bulls eye
            class_id = "bullseye" 

        elif reply =="38":
            class_id = "right"
            
        elif reply =="39":
            class_id = "left"
        
        img_file_name = f'i{image_count}_{class_id}.jpg'
        cv2.imwrite(os.path.join(img_directory, img_file_name), image)
        image_sender.close()
        return class_id
    
    except Exception as e:
        print(f"[ERROR] Image processing failed: {str(e)}")
        

if __name__=="__main__":
    stm = serial.Serial()
    stm.baudrate = 115200
    stm.port = "/dev/ttyUSB0"
    print(stm.open())
    print("[MAIN][SUCCESSFUL CONNECTION] STM ready.\n")
    
    camera = PiCamera()
    print("[MAIN][SUCCESSFUL CONNECTION] PiCamera ready.\n")
   
    
    init = ['US025'] # initialise the robot

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

    instr_list = []
    
    img1 = "left"    
    img2 = "left"
    
    move_stm(init)
    image = take_pic()
    img1 = process_image(image)
    
    if "right" in img1:
        move_stm(case_r)

    elif "left" in img1:
        move_stm(case_l)
    
    image2 = take_pic()
    img2 = process_image(image2)  
    
    # Checking if the first image is left and the second image is left.       
    if "left" in img1 and "left" in img2:
        move_stm(case_ll) 

    # Checking if the first image is left and the second image is right.       
    if "left" in img1 and "right" in img2:
        move_stm(case_lr) 
  
    # Checking if the first image is right and the second image is left.       
    if "right" in img1 and "left" in img2:
        move_stm(case_rl)
    
    # Checking if the first image is right and the second image is right. 
    if "right" in img1 and "right" in img2:
        move_stm(case_rr)