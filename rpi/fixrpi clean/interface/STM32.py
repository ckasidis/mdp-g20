# ===============================================================
# Script to manage communication with STM32F Board 
# ===============================================================

import serial
import time

class STM32(object):

	# Initialise the connection with STM32F Board
	# Check the connection port again, baud rate = 115200
	def __init__(self, port='/dev/ttyUSB0'):
		self.port = port
		self.baudrate = 115200
		self.isConnected = False

	def connect(self):
		while not self.isConnected:
			try:
				print("[STM32] Establishing connection with STM32 Board")

				# Create a Serial instance named 'ser'
				self.ser = serial.Serial(self.port, self.baudrate, timeout = 20)
				# Check if the serial instance is open
				if (self.ser.is_open):
					print("[STM32][SUCCESSFUL CONNECTION] Successfully established connection with STM32 Board.")
					self.isConnected = True

			except Exception as e:
				print(f"[STM32][ERROR] Unable to establish connection with STM32 Board: {str(e)}")
				# Retry to connect
				print("[STM32] Retrying to connect with STM32 Board")
				time.sleep(1)

	def disconnect(self):
		try:
			if (self.ser): # Check there is a serial instance created
				print("[STM32][TERMINATION] Disconnecting from STM32 Board")
				self.ser.close()
				self.isConnected = False
		except Exception as e:
			print(f"[STM32][ERROR]: Unable to disconnect from STM32 Board: {str(e)}") 


	# Getter method - to check if connection with STM32F board is established
	def getisConnected(self):
		return self.isConnected

	# Read and process message
	def read(self):
		try:
			data = self.ser.read().decode("UTF-8")
			temp = self.ser.read()
			if data == '': # No data read
				return "No reply"
			print(f"[STM32][MESSAGE RECVD] {data}")
			return data
		except Exception as e:
			print(f"[STM32][ERROR] STM32 Board read error: {str(e)}")


	# Write message
	def write(self, message):
		try:
			# Ensure connection is established before sending a message
			if self.isConnected:
				self.ser.write(message.encode('UTF-8'))
				print(f"[STM32][MESSAGE SENT] {message}")
			else:
				print("[STM32][ERROR] Connection with STM32 board is not established")

		except Exception as e:
			print("[STM32][ERROR] Unable to send message from STM32: %s" % str(e))





