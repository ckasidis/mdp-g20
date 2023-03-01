import serial
import time
from colorama import *
init(autoreset=True)

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

UUID = "00001101-0000-1000-8000-00805F9B34FB"
ANDROID_SOCKET_BUFFER_SIZE = 2048


WIFI_IP = "192.168.20.1"
WIFI_PORT = 3004
ALGORITHM_SOCKET_BUFFER_SIZE = 300


class Algo:
    def __init__(self, ip=WIFI_IP, port=WIFI_PORT):
        self.ip = ip
        self.port = port
        print(f"Listening at IP: {self.ip}")
        self.connect = None
        self.client = None
        self.address = None

        self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connect.bind((self.ip, self.port))
        self.connect.listen(1)

    def connect_ALG(self):
        while True:
            retry = False

            try:
                print('[ALG-CONN] Listening for ALG connections...')

                if self.client is None:
                    self.client, self.address = self.connect.accept()
                    print('[ALG-CONN] Successfully connected with ALG: %s' % str(self.address))
                    retry = False

            except Exception as e:
                print('[ALG-CONN ERROR] %s' % str(e))

                if self.client is not None:
                    self.client.close()
                    self.client = None
                retry = True

            if not retry:
                break

            print('[ALG-CONN] Retrying connection with ALG...')
            time.sleep(1)

    def disconnect_all(self):
        try:
            if self.connect is not None:
                self.connect.shutdown(socket.SHUT_RDWR)
                self.connect.close()
                self.connect = None
                print('[ALG-DCONN] Disconnecting Server Socket')

            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print('[ALG-DCONN] Disconnecting Client Socket')

        except Exception as e:
            print('[ALG-DCONN ERROR] %s' % str(e))

    def disconnect_ALG(self):
        try:
            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print('[ALG-DCONN] Disconnecting Client Socket')

        except Exception as e:
            print('[ALG-DCONN ERROR] %s' % str(e))

    def read_from_ALG(self):
        try:
            msg = self.client.recv(ALGORITHM_SOCKET_BUFFER_SIZE)
            data = msg.decode()
            print("Received command:", data)
            if len(data) > 0:
                return data
            return None

        except Exception as e:
            print('[ALG-READ ERROR] %s' % str(e))
            raise e

    def write_to_ALG(self, message):
        try:
            self.client.send(message)
        except Exception as e:
            print('[ALG-WRITE ERROR] %s' % str(e))
            raise e

class Android:
    def __init__(self):
        
        self.server = None
        self.client = None

        print('Starting Bluetooth')
        os.system('sudo hciconfig hci0 piscan')
        self.server = BluetoothSocket(RFCOMM)
        self.server.bind(("",PORT_ANY))
        self.server.listen(PORT_ANY)
        print('[TEST] sockname: ' + str(self.server.getsockname()))
        self.port = self.server.getsockname()[1]

        advertise_service(
            self.server, 'MDP Team 20',
            service_id=UUID,
            service_classes=[UUID, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
        )
        print('[BT] Waiting for BT connection on RFCOMM channel %d' % self.port)

    def connect_AND(self):
        while True:
            retry = False

            try:
                print('[AND-CONN] Connecting to AND...')
                if self.client is None:
                    self.client, address = self.server.accept()
                    print('[AND-CONN] Successful connected with AND: %s ' % str(address))
                    retry = False

            except Exception as e:
                print('[AND-CONN ERROR] %s' % str(e))
                if self.client is not None:
                    self.client.close()
                    self.client = None
                retry = True

            if not retry:
                break
            print('[AND-CONN] Retrying connection with AND...')

    def disconnect_AND(self):
        try:
            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print('[AND-DCONN] Disconnecting Client Socket')
        except Exception as e:
            print('[AND-DCONN ERROR] %s' % str(e))

    def disconnect_all(self):
        try:
            if self.client is not None:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                print('[AND-DCONN] Disconnecting Client Socket')

            if self.server is not None:
                self.server.shutdown(socket.SHUT_RDWR)
                self.server.close()
                self.server = None
                print('[AND-DCONN] Disconnecting Server Socket')
        except Exception as e:
            print('[AND-DCONN ERROR] %s' % str(e))

    def read_from_AND(self):
        try:
            msg = self.client.recv(ANDROID_SOCKET_BUFFER_SIZE).strip()
            print(msg)
            if msg is None:
                return None
            if len(msg) > 0:
                return msg
            return None
        except BluetoothError as e:
            print('[AND-READ ERROR] %s' % str(e))
            raise e

    def write_to_AND(self, message):
        try:
            self.client.send(message)

        except BluetoothError as e:
            print('[AND-WRITE ERROR] %s' % str(e))
            raise e

class IMAGEREC:
    def __init__(self):
        self.sender = imagezmq.ImageSender(connect_to='tcp://192.168.20.25:5555') #Connection to Image Processing Server
        self.rpi_name = socket.gethostname()
        self.camera = PiCamera(resolution=(640, 640)) #Max resolution 2592,1944

    def takePic(self):
        self.rawCapture = PiRGBArray(self.camera)
        self.camera.capture(self.rawCapture, format="bgr")
        self.image = self.rawCapture.array
        self.rawCapture.truncate(0)
        self.reply = self.sender.send_image(self.rpi_name, self.image)
        self.reply = str(self.reply.decode())
        print('IMG REC Response message\t: ' + self.reply)
        return self.reply

class STM:
    def __init__(self):
        self.port = SERIAL_PORT
        self.baud_rate = BAUD_RATE
        self.STM_connection = None

    def connect_STM(self):
        print('[STM-CONN] Waiting for serial connection...')
        while True:
            retry = False
            try:
                self.STM_connection = serial.Serial(self.port, self.baud_rate)
                if self.STM_connection is not None:
                    print('[STM-CONN] Successfully connected with STM:')
                    retry = False
            except Exception as e:
                print('[STM-CONN ERROR] %s' % str(e))
                retry = True
            if not retry:
                break
            print('[STM-CONN] Retrying connection with STM...')
            time.sleep(1)

    def disconnect_STM(self):
        try:
            if self.STM_connection is not None:
                self.STM_connection.close()
                self.STM_connection = None
                print('[STM-DCONN ERROR] Successfully closed connection')

        except Exception as e:
            print('[STM-DCONN ERROR] %s' % str(e))

    def read_from_STM(self):
        print("Reading")
        try:
            self.STM_connection.flush()
            get_message = self.STM_connection.read(9)
            print(get_message)
            if len(get_message) > 0:
                return get_message
            return None

        except Exception as e:
            print('[STM-READ ERROR] %s' % str(e))
            raise e

    def write_to_STM(self, message):
        try:
            if self.STM_connection is None:
                print('[STM-CONN] STM is not connected. Trying to connect...')
                self.connect_STM()

            print('In STM: write to STM method: before Transmitted to STM:')
            print('\t %s' % message)
            self.STM_connection.write(message)
            print(message.decode()+" sent")
            print('In STM: write to STM method: after Transmitted to STM')

        except Exception as e:
            print('[STM-WRITE Error] %s' % str(e))
            raise e
        
    def move(self, instr):
        print("move()")
        self.write_to_STM(instr.encode())
        while True:
            print("move() while loop")
            bytesToRead = self.STM_connection.inWaiting()
            raw_dat = self.STM_connection.read(1)
            print("raw_dat: " + str(raw_dat))
            dat = raw_dat.strip().decode()
            if dat == 'R':
                print("received R reply from STM")
                break
        print("exiting move while loop")