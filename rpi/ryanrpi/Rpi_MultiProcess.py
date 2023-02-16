from serial import *
from AlgoInterface import Algo
from AndroidInterface import Android
from STMInterface import STM
from colorama import *
from multiprocessing import Process, Value, Queue, Manager
import time
from datetime import datetime
import sys 
from picamera import PiCamera
import socket
import cv2
import imagezmq


from picamera.array import PiRGBArray

init(autoreset=True)
#print(sys.version)
#print(sys.path)

class MultiProcess:
    def __init__(self):
        self.AND = Android()
        self.ALG = Algo()
        self.STM = STM()

        self.manager = Manager()

        self.to_AND_message_queue = self.manager.Queue()
        self.message_queue = self.manager.Queue()
    
        
        self.read_AND_process = Process(target=self._read_AND)
        self.read_ALG_process = Process(target=self._read_ALG)
        self.read_STM_process = Process(target=self._read_STM)

        self.write_AND_process = Process(target=self._write_AND)
        self.write_process = Process(target=self._write_target)
        print(Fore.LIGHTGREEN_EX + '[MultiProcess] MultiProcessing initialized')

        self.dropped_connection = Value('i', 0)

        self.sender = None

        self.image_queue = self.manager.Queue()
        self.image_process = Process(target = self._take_pic)
        
        
        self.processes = []
        self.processes.append(self.read_AND_process)
        self.processes.append(self.read_ALG_process)
        self.processes.append(self.read_STM_process)
        self.processes.append(self.write_AND_process)
        self.processes.append(self.write_process)


    def start(self):
        try:
            self.AND.connect_AND()
            self.ALG.connect_ALG()
            self.STM.connect_STM()
            
            self.read_AND_process.start() #start() refers to Process object to start the process
            self.read_ALG_process.start()
            self.read_STM_process.start()
    
            self.write_AND_process.start()
            self.write_process.start()
            
            startComms_dt = datetime.now().strftime('%d-%b-%Y %H:%M%S')
            print(Fore.LIGHTGREEN_EX + str(startComms_dt) + '| [MultiProcess] Communications started. Reading from STM, Algorithm & Android')
            time.sleep(1)
            self.image_process.start()
            for process in self.processes:
                process.join()

        except Exception as e:
            print(Fore.RED + '[MultiProcess-START ERROR] %s' % str(e))
            raise e

    def _format_for(self, target, message):
        return {
            'target': target,
            'payload': message,
        }

    def _read_AND(self):
        while True:
            try:
                message = self.AND.read_from_AND()
                print("Reading from AND")
                if message is None:
                    continue

                message_list = message.decode().splitlines()
                print(f"AND_MESSAGE: {message_list}")
                for msg in message_list:
                    if len(msg) != 0:

                        messages = msg.split('|', 1)

                        if messages[0] == 'ALG':
                            print(Fore.WHITE + 'AND > %s , %s' % (str(messages[0]), str(messages[1])))
                            assert isinstance(messages, object)
                            self.message_queue.put_nowait(self._format_for(messages[0], (messages[1]).encode()))
                            print('queued')
                        else:
                            print(Fore.WHITE + 'AND > %s , %s' % (str(messages[0]), str(messages[1])))
                            self.message_queue.put_nowait(self._format_for(messages[0], messages[1].encode()))

            except Exception as e:
                print(Fore.RED + '[MultiProcess-READ-AND ERROR] %s' % str(e))
                break
    
    def _read_ALG(self):
        while True:
            try:
                message = self.ALG.read_from_ALG()
                print(message)
                if message is None:
                    continue
                message_list = message.splitlines()
                for msg in message_list:
                    if len(msg) != 0:

                        messages = msg.split('|', 1)

                        # Message format for Image Rec: RPI|
                        if messages[0] == 'RPI':
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s, %s' % (str(messages[0]), 'take pic'))
                            self.image_queue.put_nowait('take')
                        elif messages[0] == 'RPI_END':
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s' % (str(messages[0])))
                            print("RPI ENDING NOW...")
                            sys.exit()
                        elif messages[0] == 'AND_PATH':
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s , %s' % (str(messages[0]), str(messages[1])))
                            self.to_AND_message_queue.put_nowait(messages[1].encode())
                        elif messages[0] == 'AND_IMAGE':
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s , %s' % (str(messages[0]), str(messages[1])))
                            self.to_AND_message_queue.put_nowait(messages[1].encode())
                        else:
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s , %s' % (str(messages[0]), str(messages[1])))
                            self.message_queue.put_nowait(self._format_for(messages[0], messages[1].encode()))

            except Exception as e:
                print(Fore.RED + '[MultiProcess-READ-ALG ERROR] %s' % str(e))
                break

    def _read_STM(self):
        print("In STM Read Func")
        while True:
            try:
                message = self.STM.read_from_STM()

                if message is None:
                    continue
                print(Fore.LIGHTCYAN_EX + "STM Message received " + message.decode())
                message_list = message.decode().splitlines()
                for msg in message_list:
                    if len(msg) != 0:
#                         print("msg receive from stm: "+msg)
                        messages = msg.split('|', 1)

                        if messages[0] == 'AND':
                            print(Fore.LIGHTRED_EX + 'STM > %s , %s' % (str(messages[0]), str(messages[1])))
                            self.to_AND_message_queue.put_nowait(messages[1].encode())
                            
                        elif messages[0] == 'ALG':
                            print(Fore.LIGHTRED_EX + 'STM > %s , %s' % (str(messages[0]), str(messages[1])))
                            self.message_queue.put_nowait(self._format_for(messages[0], (messages[1]).encode()))
                        
                        elif str(messages[0]) == "\x00K":
                            messages[0] = 'K'
                            print(Fore.LIGHTRED_EX + 'STM > ALG | %s' % (str(messages[0])))
                            self.message_queue.put_nowait(self._format_for('ALG', ('K\n').encode()))
                        else:
                            print(Fore.LIGHTBLUE_EX + '[Debug] Message from STM: %s' % str(messages))

            except Exception as e:
                print(Fore.RED + '[MultiProcess-READ-STM ERROR] %s' % str(e))
                break

    def _write_AND(self):
        while True:
            try:
                if not self.to_AND_message_queue.empty():
                    message = self.to_AND_message_queue.get_nowait()
                    self.AND.write_to_AND(message)
            except Exception as e:
                print(Fore.RED + '[MultiProcess-WRITE-AND ERROR] %s' % str(e))
                break

    def _write_target(self):
        while True:
            target = None
            try:
                if not self.message_queue.empty():
                    message = self.message_queue.get_nowait()
                    print("msg :"+str(message))    
                    target, payload = message['target'], message['payload']
                    print(payload)
                    if target == 'ALG':
                        self.ALG.write_to_ALG(payload)
                        
                        print('once')
                        print('sending to algo')
                        time.sleep(0.5)
                    elif target == 'STM':
                        print(Fore.LIGHTCYAN_EX + 'To STM: before write to STM method')
#                         steps = ""
#                         for i in range(20):
#                             steps+= "a"
#                         for i in len(payload):
#                             steps[i] = payload[i]
#                         print(len(steps))
                        self.STM.write_to_STM(payload)
                        print(Fore.LIGHTCYAN_EX + 'To STM: after write to STM method')
                    elif target == 'AND_PATH' or target == 'AND':
                        time.sleep(1)
                        self.AND.write_to_AND(payload)
                    else:
                        continue

            except Exception as e:
                print(Fore.RED + '[MultiProcess-WRITE-%s ERROR] %s' % (str(target), str(e)))

                if target == 'STM':
                    self.dropped_connection.value = 0

                elif target == 'ALG':
                    self.dropped_connection.value = 1

                break

    def _take_pic(self):
            # Start the Image Rec process
            self.sender = imagezmq.ImageSender(connect_to='tcp://192.168.13.21:5555') #Connection to Image Processing Server
            while True:
                try:
                    if not self.image_queue.empty():
                        test = self.image_queue.get_nowait()
                        self.rpi_name = socket.gethostname()
                        self.camera = PiCamera(resolution=(640, 640)) #Max resolution 2592,1944
                        self.rawCapture = PiRGBArray(self.camera)

                        self.camera.capture(self.rawCapture, format="rgb")
                        self.image = self.rawCapture.array
                        self.rawCapture.truncate(0)

                        #Reply received from the Image Processing Server
                        self.reply = self.sender.send_image(self.rpi_name, self.image)
                        self.reply = str(self.reply.decode())
                        print(Fore.LIGHTYELLOW_EX + 'Reply message: ' + self.reply)

                        # #Messages sent to ALG & AND')
                        if self.reply == 'n':
                            self.reply = 'n'
                            self.message_queue.put_nowait(self._format_for('ALG',(self.reply).encode()))
                            print(Fore.LIGHTYELLOW_EX + 'Message send across to ALG: ' + self.reply)
                            
                        else:
#                             #msg format to AND: IMG-OBSTACLE_ID-IMG_ID e.g. "IMG-2-31"
                            self.reply += '\n'
                            print(self.reply)
                            self.message_queue.put_nowait(self._format_for('ALG',self.reply.encode()))
                            print(Fore.LIGHTYELLOW_EX + 'Message send across to ALG: ' + self.reply)

                        self.camera.close()
                
                except Exception as e:
                    print(Fore.RED + '[MultiProcess-PROCESS-IMG ERROR] %s' % str(e))

