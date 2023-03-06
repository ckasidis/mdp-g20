import time, signal, base64, os, glob
import socket
import imagezmq, cv2
from picamera import PiCamera
from picamera.array import PiRGBArray

img_directory = "/home/pi/mdp-g20/fixrpi/picamera_images/task1/"
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

def readMsg(queue, interface):
	''' Read and put message into the queue'''
	while True:
		try:
			msg = interface.read()
			if msg is None:
				continue
			queue.put(msg)
		except Exception as e:
			print(f"[READ ERROR]: {str(e)}")

def takePic():
	''' Take photo using PiCamera'''
	try:
			rawCapture = PiRGBArray(camera)
			camera.capture(rawCapture, format = 'bgr')
			image = rawCapture.array
			print("[TAKE PIC] Image successfully taken.")

	except Exception as e:
			print(f"[TAKE PIC][ERROR] Unable to take pic: {str(e)}")
	return image

def process_image(image):
	''' Processing image - send it to the image processing server'''

	# Initialise the ImageSender object with the socket address of the server
	start = time.time()
	print(f"\n[IMG REC] Setting up the ImageSender object at {image_processing_server_url}")
	image_sender = imagezmq.ImageSender(connect_to = image_processing_server_url)
	print(f"[IMG REC][SUCCESSFUL CONNECTION] Setup completed!")
	print(f"[IMG REC][TIME] {round(time.time()-start,3)} seconds to setup the IMG REC")

	global image_count, image_id_lst
	try:
		print("[IMG REC] Sending image to image processing server")
		start = time.time()
		rpi_name = socket.gethostname() # send RPi hostname with each image
		reply = image_sender.send_image(rpi_name, image)
		print(f"[IMG REC][TIME] {round(time.time()-start,3)} seconds to send the image and receive response")
		reply = reply.decode('utf-8')

		if reply == "n":  # no image detected
			print("\n[IMG REC][OUTPUT] No image detected.") 
			id_string_to_android = f"n"

		elif reply == "00" or reply=='0': #bulls eye
			id_string_to_android = f"00" 
			print("\n[IMG REC][OUTPUT] Bulls eye detected.")

		else:
			image_count += 1
			id_string_to_android = f"{reply}"
			# Save the image
			img_file_name = f'i{image_count}_{reply}.jpg'
			cv2.imwrite(os.path.join(img_directory, img_file_name), image)
			print(f"\n[IMG REC][OUTPUT] #{image_count} Detected Image ID {id_string_to_android}")
			print(f'[IMG REC][SAVE] The captured image is stored on RPi at ./picamera_images/{img_file_name}\n')                              

		image_sender.close()
		print(f'[IMG REC][TERMINATION] Closing ImageSender object at {image_processing_server_url}\n')
		return id_string_to_android

	except Exception as e:
		print(f"[Error] Image processing failed: {str(e)}")

# @break_after(3)
def readSTM(command):
	''' Read the ACK ('R') from STM'''
	start = time.time()
	data = ""
	while True:
		data = interfaces[STM].read()
		print(f"[STM] Data recvd from STM32: {data}")
		if data:
		# if data == "R":
			print(f"\n[STM][TIME] {round(time.time()-start,3)} seconds to receive ACK from STM")
			return
	# if data == "No reply":
	# 	interfaces[STM].write(command)
	# 	time.sleep(1)
	# 	interfaces[STM].write(STM_STOP)
	# 	readSTM(command)
        