import imagezmq
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import time, signal

img_directory = "/home/pi/rpi/picamera_images/task2/"
image_processing_server_url = "tcp://192.168.20.25:5555"
image_count = 0 # keep track of the images detected

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

def takePic():
    ''' Take photo'''
    try:
        rawCapture = PiRGBArray(camera)
        camera.capture(rawCapture, format = 'bgr')
        image = rawCapture.array
        print("[MAIN] Image successfully taken.")
        #cv2.imwrite("test.jpg", image)
    except Exception as e:
        print(f"[ERROR] Unable to take pic: {str(e)}")
    
    return image

def process_image(image):
    ''' Processing image - send it to the image processing server'''
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
            result = f"picture : right"

        else:
            result = f"picture: nothing"

        image_sender.close()
        return result

    except Exception as e:
        print(f"[Error] Image processing failed: {str(e)}")

def readSTM(command):
    data = ""
    while True:
        data = interfaces[STM].read()
        print(f"DATA FROM STM: {data}")
        if data == "R":
            return
