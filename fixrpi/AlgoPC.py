# ===============================================================
# Script to manage communication with ALgo PC
# ===============================================================

from pickle import TRUE
import time
import socket 
import logging
import os

class AlgoPC(object):

	# Initialise the connection with the Algo PC
	def __init__(self):
		self.isConnected = False
		self.client = None
		self.addr = None
		HOST = '192.168.20.25' # Server IP or Hostname
		self.PORT = 12345  # Pick an open Port (1000+ recommended), must match the client sport
		self.sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print('Socket created')
        # managing error exception
		try:
			self.sever.bind((HOST, self.PORT))
		except socket.error:
			print ('Bind failed ')


	# Getter method to check is connection is established
	def getisConnected(self):
		return self.isConnected

	def connect(self):
		print(f"Waiting for connection with ALgo PC")
		while self.isConnected == False:
			try:
				if self.client is None:
					# Accepts the connection
					self.sever.listen(5)
					print ('Socket awaiting messages')
					self.client, self.addr = self.sever.accept()
					print ('Algo PC Connected')
					self.isConnected = True

			except Exception as e:
				print(f"[ERROR] Unable to establish connection with Algo PC")
				self.client.close()
				self.client = None
				# Retry to connect
				print("Retrying to connect with Android Tablet ...")
				time.sleep(1)
				self.connect()


	def disconnect(self):
		try:
			print("Algo PC: Shutting down Server ...")
			self.server.close()
			self.server = None
			print("Algo PC: Shutting down Client ...")
			self.client.close()
			self.client = None
			self.isConnected = False
		except Exception as e:
			print("f[ERROR]: Unable to disconnect from Android: {str(e)}")
			os.system('sudo fuser -k %d/tcp' % (self.PORT))

	def read(self):
		try:
			while True:
				msg = self.client.recv(1024).strip().decode('utf-8')
				if len(msg) == 0:
					break
				print(f"[FROM ALGOPC] {msg}")
				return msg

		except Exception as e:
			print(f"[ERROR] Android read error: {str(e)}")
			# Retry connection if Android gets disconnected
			try:
				self.sever.getpeername()
			except:
				self.client.close()
				self.isConnected = False
				self.client = None
				print("Retrying to connect with Android Tablet ...")
				self.connect()
				print("Trying to read message from Android again...")
				self.read()
		return msg

	def write(self, message):
		try:
			message = message.encode("utf-8")
			if self.isConnected:
				self.client.send(message)
				print(f"[SENT TO Algo PC]: {message}")
			else:
				print("[Error]  Connection with Android Tablet is not established")

		except Exception as e:
			print(f"[ERROR] Algo PC write error: {str(e)}")
			# Retry connection if Android gets disconnected
			try:
				self.sever.getpeername()
			except:
				self.client.close()
				self.isConnected = False
				self.client = None
				print("Retrying to connect with Android Tablet...")
				self.connect()
				print("Trying to send the message to Android again...")
				write(self,message) # try writing again




