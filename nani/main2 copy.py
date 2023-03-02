import socket
from bluetooth import *
import os
import time
import serial
from picamera import PiCamera
import imagezmq

class Task1:
    def __init__():
        #ANDROID CONFIGs
        self.UUID = "00001101-0000-1000-8000-00805F9B34FB"
        self.ANDROID_SOCKET_BUFFER_SIZE = 2048
        self.AND_server = None
        self.AND_client = None

        #ALGO CONFIGs
        self.ALGO_IP = "192.168.20.1"
        self.ALGO_PORT = 3004
        self.ALGORITHM_SOCKET_BUFFER_SIZE = 1000
        self.ALGO_connect = None
        self.ALGO_client = None
        self.ALGO_address = None
        self.AND_port = None

        #STM CONFIGs
        self.STM_SERIAL_PORT = '/dev/ttyUSB0'
        self.STM_BAUD_RATE = 115200
        self.STM_connection = None

        #IMG CONFIGs
        self.IMG_sender = None

        #RUNNING VARIABLES
        self.RUN_msg_from_AND = None
        self.RUN_msg_from_ALG = None
        self.RUN_command_list = None
        self.RUN_obstacle_list = None


    def start_AND(self):
        ''' Start Android Bluetooth Connection Service'''
        try:
            print('Starting Bluetooth')
            os.system('sudo hciconfig hci0 piscan')
            self.AND_server = BluetoothSocket(RFCOMM)
            self.AND_server.bind(("",PORT_ANY))
            self.AND_server.listen(PORT_ANY)
            self.AND_port = self.AND_server.getsockname()[1]

            advertise_service(
                self.AND_server, 'MDP Team 20',
                service_id=UUID,
                service_classes=[self.UUID, SERIAL_PORT_CLASS],
                profiles=[SERIAL_PORT_PROFILE],
            )

            print('Waiting for BT connection on RFCOMM channel %d' % AND_port)
        except Exception as err:
            print('[Main.py, start_AND() ERROR] {}'.format(str(err)))

    def start_ALG(self):
        ''' Start Algorithm PC WiFi service'''
        try:
            print(f"\nListening at IP: {ALGO_IP}")
            self.ALGO_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ALGO_connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ALGO_connect.bind((self.ALGO_IP, self.ALGO_PORT))
            self.ALGO_connect.listen(1)
        except Excpetion as err:
            print('[Main.py, start_ALG() ERROR] {}'.format(str(err)))

    def connect_AND(self):
        ''' Connect to Android Tablet'''
        while True:
                retry = False

                try:
                    print('[Main.py, connect_AND()] Connecting to AND...')

                    if self.AND_client is None:
                        self.AND_client, address = self.AND_server.accept()
                        print('[Main.py, connect_AND()] Successful connected with AND: %s ' % str(address))
                        retry = False

                except Exception as e:
                    print('[Main.py, connect_AND() ERROR] %s' % str(e))

                    if self.AND_client is not None:
                        self.AND_client.close()
                        self.AND_client = None

                    retry = True

                if not retry:
                    break

                print('[Main.py, connect_AND()] Retrying connection with AND...')

    def connect_ALG(self):
        ''' Connect to ALG PC'''
        while True:
                retry = False

                try:
                    print('[Main.py, connect_ALG()] Listening for ALG connections...')

                    if self.ALGO_client is None:
                        self.ALGO_client, self.ALGO_address = self.ALGO_connect.accept()
                        print('[Main.py, connect_ALG()] Successfully connected with ALG: %s' % str(self.ALGO_address))
                        retry = False

                except Exception as e:
                    print('[Main.py, connect_ALG() ERROR] %s' % str(e))

                    if self.ALGO_client is not None:
                        self.ALGO_client.close()
                        self.ALGO_client = None
                    retry = True

                if not retry:
                    break

                print('[Main.py, connect_ALG()] Retrying connection with ALG...')
                time.sleep(1)

    def connect_STM(self):
        ''' Connect to STM Board via Serial USB'''
        print('[Main.py, connect_STM()] Waiting for serial connection...')
        while True:
            retry = False

            try:
                self.STM_connection = serial.Serial(self.STM_SERIAL_PORT, self.STM_BAUD_RATE)

                if self.STM_connection is not None:
                    print('[Main.py, connect_STM()] Successfully connected with STM:')
                    retry = False

            except Exception as e:
                print('[Main.py, connect_STM() ERROR] %s' % str(e))
                retry = True

            if not retry:
                break

            print('[Main.py, connect_STM()] Retrying connection with STM...')
            time.sleep(1)
        
    def disconnect_AND(self):
        try:
            if self.AND_client is not None:
                self.AND_client.shutdown(socket.SHUT_RDWR)
                self.AND_client.close()
                self.AND_client = None
                print('[AND-DISCONN] Disconnecting Client Socket')

            if self.AND_server is not None:
                self.AND_server.shutdown(socket.SHUT_RDWR)
                self.AND_server.close()
                self.AND_server = None
                print('[AND-DISCONN] Disconnecting Server Socket')

        except Exception as e:
            print('[AND-DISCONN ERROR] %s' % str(e))

    def disconnect_ALG(self):
        try:
            if self.ALGO_connect is not None:
                self.ALGO_connect.shutdown(socket.SHUT_RDWR)
                self.ALGO_connect.close()
                self.ALGO_connect = None
                print('[ALG-DCONN] Disconnecting Server Socket')

            if self.ALGO_client is not None:
                self.ALGO_client.shutdown(socket.SHUT_RDWR)
                self.ALGO_client.close()
                self.ALGO_client = None
                print('[ALG-DCONN] Disconnecting Client Socket')

        except Exception as e:
            print('[ALG-DCONN ERROR] %s' % str(e))

    def disconnect_STM(self):
        try:
            if self.STM_connection is not None:
                self.STM_connection.close()
                self.STM_connection = None
                print('[STM-DCONN ERROR] Successfully closed connection')

        except Exception as e:
            print('[STM-DCONN ERROR] %s' % str(e))

    def read_AND(self):
        ''' Read obstacles to pass to ALG'''
        print("Awaiting Obstacles from ANDROID")
        while True:
            try:
                if(self.AND_client == None):
                    self.connect_AND()

                self.RUN_msg_from_AND = self.AND_client.recv(self.ANDROID_SOCKET_BUFFER_SIZE).strip()

                if len(self.RUN_msg_from_AND) > 0 and self.RUN_msg_from_AND != None:
                    message_list = self.RUN_msg_from_AND.decode().splitlines()
                    print("[Main.py, read_AND()] message from AND: ", message_list[1])
                    self.RUN_msg_from_AND = self.RUN_msg_from_AND.decode()
                    return self.RUN_msg_from_AND;

            except BluetoothError as e:
                print('[Main.py, read_AND() ERROR] %s' % str(e))
                raise e
            
    def write_AND(self, msg):
        ''' Write and send message to AND
        No need to encode, function does it'''
        try:
            if(self.AND_client == None):
                self.connect_AND()
                
            self.AND_client.send(msg.encode()) #else if try msg

        except BluetoothError as e:
            print('[Main.py, write_AND() ERROR] %s' % str(e))
            raise e
            
    def write_ALGO(self, msg):
        ''' Write and send message to ALG
        No need to encode, function does it'''
        try:
            self.ALGO_client.send(msg.encode())

        except Exception as e:
            print('[Main.py, write_ALGO() ERROR] %s' % str(e))
            raise e
            
    def read_ALGO(self):
        ''' Read message from ALG'''
        while True:
            try:
                msg = self.ALGO_client.recv(self.ALGORITHM_SOCKET_BUFFER_SIZE)
                self.RUN_msg_from_ALG = msg.decode()
                print("Received command:", RUN_msg_from_ALG)

                if len(self.RUN_msg_from_ALG) > 0 and self.RUN_msg_from_ALG:
                    return self.RUN_msg_from_ALG

            except Exception as e:
                print('[Main.py, read_ALGO() ERROR] %s' % str(e))
                raise e

    def command_STM(self, message):
        ''' Send command to STM'''
        try:
            if self.STM_connection is None:
                print('[Main.py, command_STM()] STM is not connected. Trying to connect')
                self.connect_STM()

            print('[Main.py, command_STM()] before Transmitted to STM:')
            print('\t %s' % message)
            self.STM_connection.write(message.encode())
            print('\t',message +" sent")
            print('[Main.py, command_STM()] after Transmitted to STM')

            while True:
                if self.STM_connection is None:
                    print('[Main.py, command_STM()] STM is not connected. Trying to connect')
                    self.connect_STM()

                raw_dat = self.STM_connection.read(1)
                print("[Main.py, command_STM()] raw_dat: " + str(raw_dat))
                dat = raw_dat.strip().decode()
                if dat == 'R':
                    print("[Main.py, command_STM()] Received R reply from STM")
                    return "next"
                else:
                    print(f"[Main.py, command_STM()] Received '{dat}' as reply from STM")
                    return dat #for debugging incase receive not 'R'
                
        except Exception as e:
            print('[Main.py, command_STM() ERROR] %s' % str(e))
            raise e

    def take_pic(self):
        ''' Take Image using PiCamera'''
        self.IMG_sender = imagezmq.ImageSender(connect_to='tcp://192.168.20.25:5555') #Connection to Image Processing Server
        while True:
            try:
                rpi_name = socket.gethostname()
                camera = PiCamera(resolution=(640, 640)) #Max resolution 2592,1944
                rawCapture = PiRGBArray(camera)
                print("[Main.py, take_pic()] Connected to : ",str(rpi_name))
                camera.capture(rawCapture, format="bgr")
                image = rawCapture.array
                rawCapture.truncate(0)
                # msg_to_send_AND = 'n'
                camera.stop_preview()
                camera.close()
                print('[Main.py, take_pic()] Image :' ,image)

                reply = IMG_sender.send_image(rpi_name, image)
                reply = str(reply.decode())
                print('[Main.py, take_pic()] Reply message :' + reply)

                if reply == 'n': # no object found
                    reply = 'n'
                    print('[Main.py, take_pic()] No object found in image, response: ' + reply)
                    
                else: # object found
                    cls_id = reply
                    if len(RUN_obstacle_list)>0:
                        msg_to_send_AND = 'AND|OBS-'+str(RUN_obstacle_list[0])+'-'+str(cls_id)
                        RUN_obstacle_list.pop(0)
                        self.write_AND(msg_to_send_AND)
                    print("[Main.py, take_pic()] msg_to_send_AND: " , msg_to_send_AND)


                return msg_to_send_AND
                #time.sleep(2)
                
            
            except Exception as e:
                print('[MultiProcess-PROCESS-IMG ERROR] %s' % str(e))

    def KACHOW():
        RUN_msg_from_ALG_split = RUN_msg_from_ALG.split('$',1)

        RUN_command_list = RUN_msg_from_ALG_split[0].split(",")
        print("Commands Msg List : ", RUN_command_list)
        RUN_obstacle_list = RUN_msg_from_ALG_split[1].split(",")
        print("Obstacles Msg List : ", RUN_obstacle_list)

        for com in RUN_command_list:
            print("Running command: ", com)
            if len(com) != 0:
                com = com.split('|', 1)[1]

                if str(com[0]) == "RPI":
                    take_pic_reply = take_pic()
                    if take_pic_reply != 'n':
                        write_AND(take_pic_reply)

                elif str(com[0]) == "STM":
                    command_reply = command_STM(str(com[1]))
                    if command_reply != "next" :
                        print("STM reply error: " , command_reply)
                        break
                
                elif str(com[0]) == "RPI_END":
                    print("RPI ENDING")
                    break
                
                
        
        return None

    def start(self):

def init():
    try:
        


        start_AND()
        connect_AND()
        start_ALG()
        connect_ALG()
        connect_STM()
        print("Connection successful")

        read_AND() #RUN_msg_from_AND is returned as a string of 1 array of obstacles "[[],[],[]]"
        write_ALGO(RUN_msg_from_AND)
        read_ALGO() #RUN_msg_from_ALG is returned as a string of 2 array of commands and obstacle id
        KACHOW()

        print("END OF PATH: disconnecting")
        disconnect_ALG()
        disconnect_AND()
        disconnect_STM()

    except KeyboardInterrupt:
        disconnect_AND()
        disconnect_ALG()
        disconnect_STM() 
    except Exception as err:
        print('[Main.py, init() ERROR] {}'.format(str(err)))
        disconnect_AND()
        disconnect_ALG()
        disconnect_STM()

if __name__ == '__main__':
    configs = {
                'ANDROID':{
                        'UUID':"00001101-0000-1000-8000-00805F9B34FB",
                        'ANDROID_SOCKET_BUFFER_SIZE':2048,
                        'AND_server':None,
                        'AND_client':None },
                'ALGO':{
                        'ALGO_IP': '192.168.20.1',
                        'ALGO_PORT':3004,
                        'ALGORITHM_SOCKET_BUFFER_SIZE':1000,
                        'ALGO_connect':None,
                        'ALGO_client':None,
                        'ALGO_address':None },
                'STM':{
                    'STM_SERIAL_PORT':'/dev/ttyUSB0',
                    'STM_BAUD_RATE':115200,
                    'STM_connection':None },
                'IMG':{
                    'IMG_sender':None },
                'RUN':{
                    'RUN_msg_from_AND':None,
                    'RUN_msg_from_ALG':None,
                    'RUN_command_list':None,
                    'RUN_obstacle_list':None }
            }

    init()