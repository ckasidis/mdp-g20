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
		HOST = '192.168.20.1' # Server IP or Hostname
		self.PORT = 3004  # Pick an open Port (1000+ recommended), must match the client's port
		self.sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print('\n\n[ALGO PC] Socket created')
        # managing error exception
		try:
			self.sever.bind((HOST, self.PORT))
			self.sever.listen(1)
		except socket.error:
			print ('[ALGO PC][ERROR] Socket bind failed')


	# Getter method to check is connection is established
	def getisConnected(self):
		return self.isConnected

	def connect(self):
		print(f"\nWaiting for connection with Algo PC")
		while self.isConnected == False:
			try:
				if self.client is None:
					# Accepts the connection
					print ('[ALGO PC] Socket awaiting messages')
					self.client, self.addr = self.sever.accept()
					print (f'[ALGO PC][SUCCESSFUL CONNECTION] Connected at {HOST}:{self.port}\n\n')
					self.isConnected = True

			except Exception as e:
				print(f"[ALGO PC][ERROR] Unable to establish connection with Algo PC")
				self.client.close()
				self.client = None
				# Retry to connect
				print("[ALGO PC] Retrying to connect with Algo PC\n\n")
				time.sleep(1)
				self.connect()


	def disconnect(self):
		try:
			print("[ALGO PC] Shutting down Server ...")
			self.server.close()
			self.server = None
			print("[ALGO PC] Shutting down Client ...")
			self.client.close()
			self.client = None
			self.isConnected = False
		except Exception as e:
			print(f"[ALGO PC][ERROR]: Unable to disconnect from ALG: {str(e)}")
			os.system('sudo fuser -k %d/tcp' % (self.PORT))

	def read(self):
		try:
			while True:
				msg = self.client.recv(1024).strip().decode('utf-8')
				if len(msg) == 0:
					break
				print(f"[ALGOPC][MESSAGE RECVD] {msg}")
				return msg

		except Exception as e:
			print(f"[ALGO PC][ERROR] ALG read error: {str(e)}")
			# Retry connection if Android gets disconnected
			try:
				self.sever.getpeername()
			except:
				self.client.close()
				self.isConnected = False
				self.client = None
				print("[ALGO PC] Retrying to connect with ALG ...")
				self.connect()
				print("[ALGO PC] Trying to read message from ALG again...")
				self.read()
		return msg

	def write(self, message):
		try:
			message = message.encode("utf-8")
			if self.isConnected:
				self.client.send(message)
				print(f"[ALGO PC][MESSAGE SENT] {message}")
			else:
				print("[ALGO PC][ERROR] Connection with ALG is not established")

		except Exception as e:
			print(f"[ALGO PC][ERROR] Algo PC write error: {str(e)}")
			# Retry connection if Android gets disconnected
			try:
				self.sever.getpeername()
			except:
				self.client.close()
				self.isConnected = False
				self.client = None
				print("[ALGO PC] Retrying to connect with ALG...")
				self.connect()
				print("[ALGO PC] Trying to send the message to ALG...")
				write(self,message) # try writing again




