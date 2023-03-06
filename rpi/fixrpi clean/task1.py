# Main script For Week 8 Task 

from multiprocessing import Process, Queue   
from interface.STM32 import STM32

from interface.Android import Android
from interface.AlgoPC import AlgoPC
from task1.task1_utils import readMsg, takePic, process_image, readSTM

img_directory = "/home/pi/mdp-g20/fixrpi/picamera_images/"
image_processing_server_url = "tcp://192.168.20.25:5555"
image_count = 0 # keep track of the images detected

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

				# need to adjust # IMPORTANT # 
				time.sleep(5) # IMPORTANT #
				# IMPORTANT #

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