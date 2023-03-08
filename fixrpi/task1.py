# ===============================================================================================
# Main script For Week 8 Task 
# Managing the communication between RPi and STM, RPi and Android
# ===============================================================================================
# Manage multi-thread programming
from multiprocessing import Process, Queue   
import time, signal, base64, os, glob
import socket
import imagezmq, cv2
from picamera import PiCamera
from picamera.array import PiRGBArray

from STM32 import STM32
from Android import Android
from AlgoPC import AlgoPC

# ===============================================================================================
img_directory = "/home/pi/mdp-g20/fixrpi/picamera_images/"
image_processing_server_url = "tcp://192.168.20.25:5555"
image_count = 0 # keep track of the images detected

# ===============================================================================================
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

# ===============================================================================================
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
        
# ===============================================================================================
if __name__ == '__main__':

	start = time.time()

	print("[MAIN] Initialising Multiprocessing Communication")

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
	# Connect STM first, then Android
	for interface in interfaces:
		interface.connect() 

	# Start all the processes
	android.start() 
	algoPC.start()
	print("[MAIN][SUCCESSFUL INITIALISATION] Multiprocess communication started")
	print(f"[MAIN][TIME] {round(time.time()-start ,3)} seconds to start comms..")

	# Set up PiCamera
	start = time.time()
	print("\n[MAIN] Setting up PiCamera")
	camera = PiCamera()
	print("[MAIN][SUCCESSFUL CONNECTION] PiCamera ready.\n")
	print(f"[MAIN][TIME] {round(time.time()-start ,3)} seconds to start camera")


	try:
		while True:
			# Retrieve messages
			msg = queue.get()
			
			# Algo command list
			if '$' in msg:  
				start = time.time()
			
				msg = msg.split('$')
				obslst = msg[0].split(',')
				print("[MAIN][ALG] Obstacle Traversal", obslst)
				algo_commands = msg[1].split(",")
				print("[MAIN][ALG]")
			
				print(f"[MAIN][TIME] {round(time.time()-start,3)} seconds to parse commands and obstacles")

				start = time.time()
			
				for i in algo_commands:
					queue.put(i)
					print(f"put in queue\t:{i}")
			
				print(f"[MAIN][TIME] {round(time.time()-start,3)} seconds to parse commands and obstacles")

				msg = "" # Remove this msg from the queue
				continue

			elif "|" in msg:
				idx = msg.index('|')
				command = msg[:idx+1]

			else: # No msg in the queue
				continue

			# Process the message
			content = msg[idx+1:]

			# ALG -> RPi -> STM
			if command == "STM|" : 
				start = time.time()
				
				interfaces[STM].write(content)

				# need to adjust 
				time.sleep(3) 

				readSTM(content)
			
				print(f"[MAIN][STM] Finish executing {content}")
				print(f"[MAIN][TIME] {round(time.time()-start ,3)} seconds to execute {content}")

			# ANDROID -> RPi -> ALG
			elif command == "ALGO|" : 
				interfaces[ALGOPC].write(content)

			# ALG -> RPi -> IMG REC
			elif command == "RPI|": 
				start = time.time()
				
				image = takePic()
				result_msg = process_image(image)
				# print('obst list',obslst)
				result_msg = obslst[0]+'-'+result_msg
				obslst.pop(0)
				interfaces[ANDROID].write(result_msg)	
				
				print(f"[MAIN][TIME] {round(time.time()-start ,3)} seconds to execute content")
			

	except Exception as e:
		print(f"[MAIN][ERROR] {str(e)}")
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
		print("\n\n[MAIN][TERMINATION] Camera closed.")
		print("[MAIN][TERMINATION] Android read message process terminated.")








