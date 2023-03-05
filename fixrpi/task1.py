# ==========================================================
# Main script For Week 8 Task 
# Managing the communication between RPi and STM, RPi and Android
# ===============================================================

from multiprocessing import Process, Queue   # Manage multi-thread programming
import time

from STM32 import STM32
from Android import Android
from AlgoPC import AlgoPC
# from Commands import *

import imagezmq
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray

import base64
import os
import glob
import socket

img_directory = "/home/pi/mdp-g20/fixrpi/picamera_images/"
image_processing_server_url = "tcp://192.168.20.25:5555"
image_count = 0 # keep track of the images detected

# ===============================================================================================
# Read and put message into the queue
def readMsg(queue, interface):
	while True:
		try:
			msg = interface.read()
			if msg is None:
				continue
			queue.put(msg)
		except Exception as e:
			print(f"[READ ERROR]: {str(e)}")

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
			if x == "0":
				image_sender.send_image("gg", image)
				print("sent gg for end of task")
				return
			rpi_name = socket.gethostname() # send RPi hostname with each image
			print("[MAIN] Sending image to image processing server...")
			reply = image_sender.send_image(rpi_name, image)
			reply = reply.decode('utf-8')

			if reply == "n":  # no image detected
				print("[MAIN] No image detected") 
				id_string_to_android = f"n"

			elif reply == "00": #bulls eye
				id_string_to_android = f"00" 
				print("[MAIN] Bulls eye detected.")

			else:
					image_count += 1
					id_string_to_android = f"{reply}"
					# Save the image
					img_file_name = f'i{image_count}_{reply}.jpg'
					cv2.imwrite(os.path.join(img_directory, img_file_name), image)                              

			image_sender.close()
			return id_string_to_android


	except Exception as e:
			print(f"[Error] Image processing failed: {str(e)}")

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

@break_after(5)
def readSTM(command):
	data = ""
	while True:
		data = interfaces[STM].read()
		print(f"DATA FROM STM: {data}")
		if data == "R":
			return
	# if data == "No reply":
	# 	interfaces[STM].write(command)
	# 	time.sleep(1)
	# 	interfaces[STM].write(STM_STOP)
	# 	readSTM(command)

        

# ===============================================================================================


if __name__ == '__main__':

	print("[MAIN] Initialising Multiprocessing Communication ...")

	# List of Interfaces - STM32F board, Android
	interfaces = []
	interfaces.append(STM32())
	interfaces.append(Android())
	interfaces.append(AlgoPC())

	# Index of the interfaces in the list
	STM = 0
	ANDROID = 1
	ALGOPC = 2

	# Set up a queue to support manage messages received by the interfaces
	queue = Queue()
	
	# Create Process objects
	# stm = Process(target=readMsg, args=(queue, interfaces[STM]))
	android = Process(target=readMsg, args=(queue, interfaces[ANDROID]))
	algoPC = Process(target=readMsg, args=(queue, interfaces[ALGOPC]))
    
	# Establish connections between RPi and all other interfaces
	for interface in interfaces:
		interface.connect() # connect STM first, then Android

	android.start() # Starts to receive message from Android 
	# stm.start()
	algoPC.start()
	print("[MAIN] Multiprocess communication started.")


	# Set up PiCamera
	print("[MAIN] Setting up PiCamera...")
	camera = PiCamera()
	print("[SUCCESSFUL CONNECTION] PiCamera ready.")


	try:
		while True:
			# Retrieve messages
			msg = queue.get()
			#print(f"msg get from queue: {msg}")
			# if "RPI" in msg:
			# 	print("msg")
				# interfaces[ANDROID].write("Message received")
				# break
			# Auto Mode
			if '$' in msg: #Algo command list 
				msg = msg.split('$')
				obslst = msg[0].split(',')
				print("[FROM ALGO PC] Obstacle Traversal", obslst)
				algo_commands = msg[1].split(",")
				print("[FROM ALGO PC]")
				for i in algo_commands:
					queue.put(i)
					print(f"put in queue {i}")
				msg = "" # Remove this msg from the queue
				continue
			elif "|" in msg:
				idx = msg.index('|')
				command = msg[:idx+1]

			else: # No msg in the queue
				continue

			# Process the message
			content = msg[idx+1:]

			if command == "STM|" : #Path planning to STM
				interfaces[STM].write(content)
				time.sleep(5) # need to adjust 
				readSTM(content)
				print(f"[FROM STM]: finish executing {content}")

			elif command == "ALGO|" : #Android to path planning
				interfaces[ALGOPC].write(content)

			elif command == "RPI|": #Path planing to RPi
				image = takePic()
				result_msg = process_image(x, image)
				print('obst list',obslst)
				result_msg = obslst[0]+'-'+result_msg
				obslst.pop(0)
				interfaces[ANDROID].write(result_msg)				

	except Exception as e:
		print(f"[ERROR] {str(e)}")
		for i in interfaces:
			i.disconnect()
		camera.close()

	finally:
		for i in interfaces:
			i.disconnect()
		camera.close()
		android.terminate()
		# stm.terminate()
		algoPC.terminate()
		
		# Terminate the process
		print("[MAIN] Camera closed.")
		print("[MAIN] Android read message process terminated.")








