import socket
import os
from colorama import *
init(autoreset=True)

UUID = "00001101-0000-1000-8000-00805F9B34FB"
ANDROID_SOCKET_BUFFER_SIZE = 2048
    
WIFI_IP = "192.168.20.1"
WIFI_PORT = 3004
ALGORITHM_SOCKET_BUFFER_SIZE = 600

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

### Make all the connections ###
# Connect to Android Tablet (via BT) => connect2Android()
def connect2Android():

    ## INITIALISATION ##
    try:
        server, client = None, None
        print(Fore.WHITE + '[CONNECT TO ANDROID]', 'Starting Bluetooth')
        os.system('sudo hciconfig hci0 piscan')
        server = BluetoothSocket(RFCOMM)
        server.bind(("",PORT_ANY))
        server.listen(PORT_ANY)
        print('[TEST] sockname: ' + str(server.getsockname()))
        port = server.getsockname()[1]
        advertise_service(
            server, 'MDP Team 20',
            service_id=UUID,
            service_classes=[UUID, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
        )
        print(Fore.WHITE + '[CONNECT TO ANDROID] [BT]','Waiting for BT connection on RFCOMM channel %d' % port)
    except Exception as e:
        print(Fore.RED + '[CONNECT TO ANDROID]','INITIALISATION FAILED!' ,str(e))
        
    ## CONNECTION PART
    while True:
        retry = False
        try:
            print(Fore.WHITE + '[CONNECT TO ANDROID]','Connecting to AND...')
            if client is None:
                client, address = server.accept()
                print(Fore.GREEN + '[CONNECT TO ANDROID]', 'Successful connected with AND: %s ' % str(address))
                retry = False
                return server, client

        except Exception as e:
            print(Fore.RED + '[CONNECT TO ANDROID]','CONNECTION SETUP FAILED!', str(e))
            if client is not None:
                client.close()
                client = None
            retry = True

        if not retry:
            break
        print(Fore.WHITE + '[CONNECT TO ANDROID]','Retrying connection with AND...')

# Connect to Algorithm PC (via WiFi) => connect2AlgorithmPC()
def connect2AlgorithmPC():

    ip = ip
    port = port
    print('\n\n',Fore.WHITE + '[CONNECT TO ALGO]',f"Listening at IP: {ip}")
    connect = None
    client = None
    address = None

    connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connect.bind((ip, port))
    connect.listen(1)

    while True:
        retry = False

        try:
            print(Fore.WHITE + '[CONNECT TO ALGO]','Listening for ALG connections...')

            if client is None:
                client, address = connect.accept()
                print(Fore.GREEN + '[CONNECT TO ALGO]','Successfully connected with ALG: %s' % str(address))
                retry = False

        except Exception as e:
            print(Fore.RED + '[CONNECT TO ALGO]', '%s' % str(e))

            if client is not None:
                client.close()
                client = None
            retry = True

        if not retry:
            break

        print(Fore.WHITE + '[CONNECT TO ALGO]','Retrying connection with ALG...')
        time.sleep(1)

    return connect, client

# Connect to Image Server PC (via WiFi) => connect2IR()
def connect2IR():
    sender = imagezmq.ImageSender(connect_to='tcp://192.168.20.25:5555') #Connection to Image Processing Server
    camera = PiCamera(resolution=(640, 640)) #Max resolution 2592,1944
    rpi_name = socket.gethostname()
    return sender, camera, rpi_name

# Connect to STM (via USB) => connectToSTM()
def connect2STM():
    port = SERIAL_PORT
    baud_rate = BAUD_RATE
    STM_connection = None
    print(Fore.WHITE + '[CONNECT TO STM]','Waiting for serial connection...')
    while True:
        retry = False

        try:
            STM_connection = serial.Serial(port, baud_rate)
            if STM_connection is not None:
                print(Fore.GREEN + '[CONNECT TO STM]','Successfully connected with STM')
                retry = False

        except Exception as e:
            print(Fore.RED + '[CONNECT TO STM]','CONNECTION ERROR %s' % str(e))
            retry = True

        if not retry:
            break

        print(Fore.WHITE + '[CONNECT TO STM]', 'Retrying connection with STM...')
        time.sleep(1)
    return STM_connection

### Compute Path and Commands ###
# ANDROID --sendCommands-> ALGORITHMS => sendCmds2Alg()
def read_from_AND(android_client):
    try:
        msg = android_client.recv(ANDROID_SOCKET_BUFFER_SIZE).strip()
        print(msg)
        if msg is None:
            return None

        if len(msg) > 0:
            return msg

        return None

    except BluetoothError as e:
        print('[AND-READ ERROR] %s' % str(e))
        raise e
def write_to_ALG(algo_client,message):
    try:
        algo_client.send(message)
    except Exception as e:
        print('[ALG-WRITE ERROR] %s' % str(e))
        raise e

def sendPath2Alg(android_client, algo_client):
    msg = read_from_AND(android_client)
    write_to_ALG(algo_client, msg)

# ALGORITHMS --SendAllCommands-> RASPBERRY PI => sendAllCmds2RPi()
def read_from_ALG(algo_client):
    try:
        msg = algo_client.recv(ALGORITHM_SOCKET_BUFFER_SIZE)
        data = msg.decode()
        print("Received command:", data)

        if len(data) > 0:
            return data

        return None

    except Exception as e:
        print('[ALG-READ ERROR] %s' % str(e))
        raise e
def recvAllCmdsfromALG(algo_client):
    return
    
# RASPBERRY PI <--takePic => takePicRPi()
def takePicRPi(camera, rpi_name):
    rawCapture = PiRGBArray(self.camera)
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    rawCapture.truncate(0)
    return image, rpi_name

# RASPBERRY PI --sendImage-> IMG REC PC => sendPic2IR()
def sendPic2IR(sender, image, rpi_name):
    reply = sender.send_image(rpi_name, image)
    reply = str(reply.decode())
    print(Fore.LIGHTYELLOW_EX + '[IMG REC]' + reply)
    return reply

# RASPBERRY PI --sendClassID_AND-> ANDROID => sendID2AND()
def write_to_AND(andclient,message):
    try:
        andclient.send(message)
    except BluetoothError as e:
        print('[AND-WRITE ERROR] %s' % str(e))
        raise e
def sendID2AND(and_client, obs_id, cls_id):
    message = 'OBS-'+str(obs_id)+'-'+str(cls_id)
    write_to_AND(and_client, message)

# RASPBERRY PI --SendCommand()-> STM => sendCmd2STM()
def write_to_STM(STM_connection, message):
    try:
        if STM_connection is None:
            print('[STM-CONN] STM is not connected. Trying to connect...')
            self.connect_STM()

        print('In STM: write to STM method: before Transmitted to STM:')
        print('\t %s' % message)
        STM_connection.write(message)
        print(message.decode()+" sent")
        print('In STM: write to STM method: after Transmitted to STM')

    except Exception as e:
        print('[STM-WRITE Error] %s' % str(e))
        raise e
def sendCmd2STM(STM_connection):
    write_to_STM(STM_connection, message)