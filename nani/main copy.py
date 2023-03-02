import socket
from bluetooth import *
import os
import time
import serial
from picamera import PiCamera
import imagezmq
from mdp_variables import *


def start_AND():
    try:
        print('Starting Bluetooth')
        os.system('sudo hciconfig hci0 piscan')
        AND_server = BluetoothSocket(RFCOMM)
        AND_server.bind(("",PORT_ANY))
        AND_server.listen(PORT_ANY)
        AND_port = AND_server.getsockname()[1]

        advertise_service(
            AND_server, 'MDP Team 20',
            service_id=UUID,
            service_classes=[UUID, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
        )

        print('Waiting for BT connection on RFCOMM channel %d' % AND_port)
    except Exception as err:
        print('[Main.py, start_AND() ERROR] {}'.format(str(err)))

def start_ALG():
    print(f"Listening at IP: {ALGO_IP}")
    ALGO_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ALGO_connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ALGO_connect.bind((ALGO_IP, ALGO_PORT))
    ALGO_connect.listen(1)

def connect_AND():
    while True:
            retry = False

            try:
                print('[AND-CONN] Connecting to AND...')

                if AND_client is None:
                    AND_client, address = AND_server.accept()
                    print('[AND-CONN] Successful connected with AND: %s ' % str(address))
                    retry = False

            except Exception as e:
                print('[AND-CONN ERROR] %s' % str(e))

                if AND_client is not None:
                    AND_client.close()
                    AND_client = None

                retry = True

            if not retry:
                break

            print('[AND-CONN] Retrying connection with AND...')

def connect_ALG():
    while True:
            retry = False

            try:
                print('[ALG-CONN] Listening for ALG connections...')

                if ALGO_client is None:
                    ALGO_client, ALGO_address = ALGO_connect.accept()
                    print('[ALG-CONN] Successfully connected with ALG: %s' % str(ALGO_address))
                    retry = False

            except Exception as e:
                print('[ALG-CONN ERROR] %s' % str(e))

                if ALGO_client is not None:
                    ALGO_client.close()
                    ALGO_client = None
                retry = True

            if not retry:
                break

            print('[ALG-CONN] Retrying connection with ALG...')
            time.sleep(1)

def connect_STM():
    print('[STM-CONN] Waiting for serial connection...')
    while True:
        retry = False

        try:
            STM_connection = serial.Serial(STM_SERIAL_PORT, STM_BAUD_RATE)

            if STM_connection is not None:
                print('[STM-CONN] Successfully connected with STM:')
                retry = False

        except Exception as e:
            print('[STM-CONN ERROR] %s' % str(e))
            retry = True

        if not retry:
            break

        print('[STM-CONN] Retrying connection with STM...')
        time.sleep(1)
    
def disconnect_AND():
    try:
        if AND_client is not None:
            AND_client.shutdown(socket.SHUT_RDWR)
            AND_client.close()
            AND_client = None
            print('[AND-DCONN] Disconnecting Client Socket')

        if AND_server is not None:
            AND_server.shutdown(socket.SHUT_RDWR)
            AND_server.close()
            AND_server = None
            print('[AND-DCONN] Disconnecting Server Socket')

    except Exception as e:
        print('[AND-DCONN ERROR] %s' % str(e))

def disconnect_ALG():
    try:
        if ALGO_connect is not None:
            ALGO_connect.shutdown(socket.SHUT_RDWR)
            ALGO_connect.close()
            ALGO_connect = None
            print('[ALG-DCONN] Disconnecting Server Socket')

        if ALGO_client is not None:
            ALGO_client.shutdown(socket.SHUT_RDWR)
            ALGO_client.close()
            ALGO_client = None
            print('[ALG-DCONN] Disconnecting Client Socket')

    except Exception as e:
        print('[ALG-DCONN ERROR] %s' % str(e))

def disconnect_STM():
    try:
        if STM_connection is not None:
            STM_connection.close()
            STM_connection = None
            print('[STM-DCONN ERROR] Successfully closed connection')

    except Exception as e:
        print('[STM-DCONN ERROR] %s' % str(e))

def read_AND():
    #read obstacles to pass to algo
    print("Awaiting Obstacles from ANDROID")
    while True:
        try:
            if(AND_client == None):
                connect_AND()

            RUN_msg_from_AND = AND_client.recv(ANDROID_SOCKET_BUFFER_SIZE).strip()

            if len(RUN_msg_from_AND) > 0 and RUN_msg_from_AND != None:
                message_list = RUN_msg_from_AND.decode().splitlines()
                print("MESSAGE FROM AND: ", message_list[1])
                RUN_msg_from_AND = RUN_msg_from_AND.decode()
                return RUN_msg_from_AND;

        except BluetoothError as e:
            print('[AND-READ ERROR] %s' % str(e))
            raise e
        
def write_AND(msg):
    try:
        if(AND_client == None):
            connect_AND()
            
        AND_client.send(msg)

    except BluetoothError as e:
        print('[AND-WRITE ERROR] %s' % str(e))
        raise e
        
def write_ALGO(msg):
        try:
            ALGO_client.send(msg.encode())

        except Exception as e:
            print('[ALG-WRITE ERROR] %s' % str(e))
            raise e
        
def read_ALGO():
        while True:
            try:
                msg = ALGO_client.recv(ALGORITHM_SOCKET_BUFFER_SIZE)
                RUN_msg_from_ALG = msg.decode()
                print("Received command:", RUN_msg_from_ALG)

                if len(RUN_msg_from_ALG) > 0 and RUN_msg_from_ALG:
                    return RUN_msg_from_ALG


            except Exception as e:
                print('[ALG-READ ERROR] %s' % str(e))
                raise e

def command_STM(message):
    try:
        if STM_connection is None:
            print('[STM-CONN] STM is not connected. Trying to connect...')
            connect_STM()
        print('In STM: write to STM method: before Transmitted to STM:')
        print('\t %s' % message)
        STM_connection.write(message.encode())
        print(message +" sent")
        print('In STM: write to STM method: after Transmitted to STM')
        while True:
            if STM_connection is None:
                print('[STM-CONN] STM is not connected. Trying to connect...')
                connect_STM()
            raw_dat = STM_connection.read(1)
            print("raw_dat: " + str(raw_dat))
            dat = raw_dat.strip().decode()
            if dat == 'R':
                print("received R reply from STM")
                return "next"
            else:
                return dat #for debugging incase receive not 'R'
            
    except Exception as e:
        print('[STM-WRITE Error] %s' % str(e))
        raise e

def take_pic():
        IMG_sender = imagezmq.ImageSender(connect_to='tcp://192.168.20.25:5555') #Connection to Image Processing Server
        while True:
            try:
                rpi_name = socket.gethostname()
                camera = PiCamera(resolution=(640, 640)) #Max resolution 2592,1944
                rawCapture = PiRGBArray(camera)
                print("takepic(): ",rpi_name )
                camera.capture(rawCapture, format="bgr")
                image = rawCapture.array
                rawCapture.truncate(0)
                msg_to_send_AND = 'n'
                print('self.image: ' ,image)

                reply = IMG_sender.send_image(rpi_name, image)
                reply = str(reply.decode())
                print('Reply message: ' + reply)

                if reply == 'n': # no object found
                    reply = 'n'
                    print('No object found in image: ' + reply)
                    
                else: # object found
                    cls_id = reply
                    if len(RUN_obstacle_list)>0:
                        msg_to_send_AND = 'AND|OBS-'+str(RUN_obstacle_list[0])+'-'+str(cls_id)
                        RUN_obstacle_list.pop(0)
                    print("msg_to_send_AND: " , msg_to_send_AND)

                camera.stop_preview()
                camera.close()
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
    #ANDROID CONFIGs
    UUID = "00001101-0000-1000-8000-00805F9B34FB"
    ANDROID_SOCKET_BUFFER_SIZE = 2048
    AND_server = None
    AND_client = None

    #ALGO CONFIGs
    ALGO_IP = "192.168.20.1"
    ALGO_PORT = 3004
    ALGORITHM_SOCKET_BUFFER_SIZE = 1000
    ALGO_connect = None
    ALGO_client = None
    ALGO_address = None

    #STM CONFIGs
    STM_SERIAL_PORT = '/dev/ttyUSB0'
    STM_BAUD_RATE = 115200
    STM_connection = None

    #IMG CONFIGs
    IMG_sender = None

    #RUNNING VARIABLES
    RUN_msg_from_AND = None
    RUN_msg_from_ALG = None
    RUN_command_list = None
    RUN_obstacle_list = None
    init()