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
				id_string_to_android = f"aatarget [{x},99]"

			elif reply == "00": #bulls eye
				id_string_to_android = f"aatarget [{x},{reply}]" 
				print("[MAIN] Bulls eye detected.")

			else:
					image_count += 1
					id_string_to_android = f"aatarget [{x},{reply}]"
					# Save the image
					img_file_name = f'i{image_count}_{reply}.jpg'
					cv2.imwrite(os.path.join(img_directory, img_file_name), image)                              

			image_sender.close()
			return id_string_to_android


	except Exception as e:
			print(f"[Error] Image processing failed: {str(e)}")

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
	#stm.start()
	algoPC.start()
	print("[MAIN] Multiprocess communication started.")


	# Set up PiCamera
	print("[MAIN] Setting up PiCamera...")
	camera = PiCamera()
	print("[MAIN] PiCamera ready.")

	# Initialise variables
	#msg = "PS|BW030"
	# msg = "PS|FW030,PS|BW040,PS|FL045,PS|BL030,PS|FR090,PS|BR050"
	# queue.put(msg)
	#count = 0
	try:
		while True:
			# Retrieve messages
			msg = queue.get()
			#print(f"msg get from queue: {msg}")
			if "rpi" in msg:
				print("msg")
				interfaces[ANDROID].write("Meessage received")
				break
			# Auto Mode
			if "," in msg and "|" in msg: #Algo command list 
				algo_commands = msg.split(",")
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
			if command == "PS|" : #Path planning to STM
				interfaces[STM].write(content)
				#time.sleep(5) #need to adjust 
				readSTM(content)
				print(f"[FORM STM]: finish executing {content}")

			elif command == "AP|" : #Android to path planning
				interfaces[ALGOPC].write(content)
			elif command == "AR|":
				if content[:8] == "starting":
					interfaces[ALGOPC].write(content)
				elif "reset" in content:
					interfaces[ALGOPC].write("reset")
				elif "end" in content:
					image = takePic()
					process_image(0, image)
			elif command == "PR|": #Path planing to RPi
				if content[:1] == "S":
					x = content[1:]
					interfaces[ANDROID].write(f"Taking picture for obstacle {x}")
					image = takePic()
					result_msg = process_image(x, image)
					print(result_msg)
					interfaces[ANDROID].write(result_msg)				
				elif content[:5] == "start":
					while True:
						ans = input("Enter yes to start")
						if ans == "yes":
							break
					interfaces[ANDROID].write("Start exploring")
				elif content[:1] == "O":
					x = content[1:]
					interfaces[ANDROID].write(f"Heading to obstacle {x}")
					print(f"Heading to obstacle at {x}")
				else:
					continue

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
		#stm.terminate()
		algoPC.terminate()
		  # Terminate the process
		print("[MAIN] Camera closed.")
		print("[MAIN] Android read message process terminated.")







