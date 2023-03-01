from serial import *
from algorithm_rpi.algorithm_client import Algo
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
# print(sys.version)
# print(sys.path)

class MultiProcess:
    def __init__(self):
        self.AND = Android()
        self.ALG = Algo()
        self.STM = STM()
        self.obslst = []
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
            print(Fore.GREEN + str(startComms_dt) + '| [MultiProcess] Communications started. Reading from STM, Algorithm & Android')
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
                print("Reading from ANDROID")
                if message is None:
                    continue
                message_list = message.decode().splitlines()
                print(f"AND_MESSAGE: {message_list}")
                for msg in message_list:
                    if len(msg) != 0:
                        messages = msg.split('|', 1)
                        if messages[0] == 'ALGO':
                            print(Fore.LIGHTGREEN_EX + 'AND > %s , %s' % (str(messages[0]), str(messages[1])))
                            assert isinstance(messages, object)
                            self.message_queue.put_nowait(self._format_for('ALG', (messages[1]).encode()))
                            print('queued')
                        elif messages[0] == 'RPI':
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s, %s' % (str(messages[0]), str(messages[1])))
                            self.image_queue.put_nowait('take')
                        elif messages[0] == 'RPI_END':
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s' % (str(messages[0])))
                            print("RPI ENDING NOW...")
                            sys.exit()
                        else:
                            print(Fore.WHITE + 'AND > %s , %s' % (str(messages[0]), str(messages[1])))
                            self.message_queue.put_nowait(self._format_for(messages[0], messages[1].encode()))

            except Exception as e:
                print(Fore.RED + '[MultiProcess-READ-AND ERROR] %s' % str(e))
                break
    
    def _read_ALG(self):
        while True:
            try:
                print("Read Command Message from ALGO")
                message = self.ALG.read_from_ALG()
                print("Message before split ",message)
                if message is None:
                    continue
                messages = message.split('$',1)
                message_list = messages[0].split(",")
                print("Command Msg List : ", message_list)
                self.obslst = messages[1].split(",")
                print("Obst Msg List : ", self.obslst)

                for msg in message_list:
                    if len(msg) != 0:
                        messages = msg.split('|', 1)
                        if messages[0] == 'RPI': # camera
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s, %s' % (str(messages[0]), str(messages[1])))
                            self.image_queue.put_nowait('take')
                        elif messages[0] == 'RPI_END': # quit
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s' % (str(messages[0])))
                            print("RPI ENDING NOW...")
                            sys.exit()
                        elif messages[0] == 'STM': # stm
                            print(Fore.LIGHTCYAN_EX + 'To STM: before move STM method')
                            self.STM.move(str(messages[1]))
                            print(Fore.LIGHTCYAN_EX + 'To STM: after move STM method')
                        else:
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s , %s' % (str(messages[0]), str(messages[1])))
                            self.message_queue.put_nowait(self._format_for(messages[0], messages[1].encode()))
                            print(Fore.LIGHTGREEN_EX + 'ALG > %s , %s' % (str('AND'), str(messages[1])))
                            self.to_AND_message_queue.put_nowait(messages[1].encode())

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
                        print('Sending to algo via _write_target()')
                        time.sleep(0.5)
                    elif target == 'STM':
                        print(Fore.LIGHTCYAN_EX + 'To STM: before move STM method')
                        self.STM.move(payload)
                        print(Fore.LIGHTCYAN_EX + 'To STM: after move STM method')
                    elif target == 'AND':
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
            self.sender = imagezmq.ImageSender(connect_to='tcp://192.168.20.25:5555') #Connection to Image Processing Server
            while True:
                try:
                    if not self.image_queue.empty():
                        test = self.image_queue.get_nowait()
                        self.rpi_name = socket.gethostname()
                        self.camera = PiCamera(resolution=(640, 640)) #Max resolution 2592,1944
                        self.rawCapture = PiRGBArray(self.camera)

                        self.camera.capture(self.rawCapture, format="bgr")
                        self.image = self.rawCapture.array
                        self.rawCapture.truncate(0)

                        self.reply = self.sender.send_image(self.rpi_name, self.image)
                        self.reply = str(self.reply.decode())
                        print('Reply message: ' + self.reply)

                        if self.reply == 'n': # no object found
                            self.reply = 'n'
                            print(Fore.LIGHTYELLOW_EX + 'Message send across to Rpi: ' + self.reply)
                            
                        else: # object found
                            cls_id = self.reply
                            if len(self.obslst)>0:
                                msg = 'AND|OBS-'+str(self.obslst[0])+'-'+str(cls_id)
                                self.obslst.pop(0)
                            self.message_queue.put_nowait(self._format_for('AND', msg.encode()))
                            print(Fore.LIGHTYELLOW_EX + 'Message send across to AND: ' + msg)

                        self.camera.close()
                        break
                
                except Exception as e:
                    print(Fore.RED + '[MultiProcess-PROCESS-IMG ERROR] %s' % str(e))
