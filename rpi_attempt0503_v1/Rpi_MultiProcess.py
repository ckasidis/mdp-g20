from serial import *
from AlgoInterface import Algo
from AndroidInterface import Android
from STMInterface import STM
from colorama import *
from multiprocessing import Process, Value, Queue, Manager, Lock
import time
from datetime import datetime
import sys 
from picamera import PiCamera
import socket
import cv2
import imagezmq
import signal
from picamera.array import PiRGBArray
init(autoreset=True)

class TimeoutException(Exception):   # Custom exception class
    pass

def break_after(seconds=2):
    def timeout_handler(signum, frame):   # Custom signal handler
        raise TimeoutException
    def function(function):
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                res = function(*args, **kwargs)
                signal.alarm(0)      # Clear alarm
                return res
            except TimeoutException:
                print (f'Oops, timeout: %s sec reached.' % seconds, function.__name__, args, kwargs)
            return
        return wrapper
    return function


class MultiProcess:
    def __init__(self):
        self.AND = Android()
        self.ALG = Algo()
        self.STM = STM()
        self.obslst = []
        self.manager = Manager()
        self.lock = True
        self.to_AND_message_queue = self.manager.Queue()
        self.message_queue = self.manager.Queue()
        self.commands = []
        
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
            
            #start() refers to Process object to start the process
            self.read_AND_process.start() 
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

                        if messages[0] == 'ALG' or messages[0] == 'ALGO':
                            print(Fore.WHITE + 'AND > %s , %s' % (str(messages[0]), str(messages[1])))
                            assert isinstance(messages, object)
                            self.message_queue.put_nowait(self._format_for('ALG', (messages[1]).encode()))
                        elif messages[0] == 'RPI_END':
                            print(Fore.WHITE + 'AND > %s , %s' % (str(messages[0]), str(messages[1])))
                            sys.exit()
                        else:
                            print(Fore.WHITE + 'AND > %s , %s' % (str(messages[0]), str(messages[1])))
                            self.message_queue.put_nowait(self._format_for(messages[0], messages[1].encode()))

            except Exception as e:
                print(Fore.RED + '[MultiProcess-READ-AND ERROR] %s' % str(e))
                break
    
    def _read_ALG_custom(self):
        while True:
            try:
                message = self.ALG.read_from_ALG()
                print("[_read_ALG] Message recvd as is", message)
                if message is None:
                    continue
                messages = message.split('$',1) # to split commands and obstacle list
                message_list = messages[0].split(",")
                print("[_read_ALG] Command Msg List : ", message_list)
                self.commands = message_list
                self.obslst = messages[1].split(",")
                print("[_read_ALG] Obstacle Traversal Order : ", self.obslst)

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
                            while True:
                                self._read_STM()
                                if not self.lock.acquire():
                                    break
                break # added the break statement to avoid infinite 'none' loop

            except Exception as e:
                print(Fore.RED + '[MultiProcess-READ-ALG ERROR] %s' % str(e))
                break

    def _read_ALG(self):
        while True:
            try:
                message = self.ALG.read_from_ALG()
                print("[_read_ALG] Message recvd as is", message)
                if message is None:
                    continue
                if "$" in message:
                    messages = message.split('$',1) # to split commands and obstacle list
                    self.obslst = messages[0].split(",")
                    print("\n[_read_ALG] Obstacle Traversal Order : ", self.obslst)

                else:
                    # message = self.ALG.read_from_ALG()
                    message_list = message.splitlines()
                    print("\n[_read_ALG] Command Msg List : ", message_list)
                    self.commands = message_list

                    for msg in message_list:
                        if len(msg) != 0:

                            messages = msg.split('|', 1)

                            # Message format for Image Rec: RPI|
                            if messages[0] == 'RPI':
                                print(Fore.LIGHTGREEN_EX + 'ALG > %s, %s' % (str(messages[0]), 'take pic'))
                                self.image_queue.put_nowait('take')
                            elif messages[0] == 'RPI_END': # end keyword
                                print(Fore.LIGHTGREEN_EX + 'ALG > %s' % (str(messages[0])))
                                print("RPI ENDING NOW...")
                                sys.exit()
                            else: # STM 
                                while True:
                                    if self.lock:
                                        print(Fore.LIGHTGREEN_EX + 'ALG > %s , %s' % (str(messages[0]), str(messages[1])))
                                        self.message_queue.put(self._format_for(messages[0], messages[1].encode()))
                                        self.lock=False
                                        break


            except Exception as e:
                print(Fore.RED + '[MultiProcess-READ-ALG ERROR] %s' % str(e))
                break

    @break_after(5)
    def _read_STM_custom(self):
        print("In STM Read Func")
        while True:
            try:
                # with self.lock:
                    message = self.STM.STM_connection.read(1).strip().decode() 
                    print(Fore.LIGHTCYAN_EX + '\n[_read_STM] Message recvd and decoded as ',str(message)) 
                    if 'R' or '\x00' or '' in message: 
                        print(Fore.LIGHTRED_EX + '\nSTM > %s , %s' % ('ALG', message))
                        self.STM.STM_connection.flush()
                        break
                        # self.message_queue.put_nowait(self._format_for('ALG', 'R'))
                    # self.lock.release()
                    
            except Exception as e:
                print(Fore.RED + '[MultiProcess-READ-STM ERROR] %s' % str(e))
                break

    def _read_STM(self):
        print("In STM Read Func")
        while True:
            try:
            #     message = self.STM.read_from_STM()
            #     message_list = message.decode().splitlines()
            #     for msg in message_list:
            #         if len(msg) != 0:
            #             messages = msg.split('|', 1)

            #             if "\x00" or "R" or "" in messages:
            #                 messages[0] = 'R'
            #                 print(Fore.LIGHTRED_EX + 'STM > ALG | %s' % (R))
            #                 self.message_queue.put_nowait(self._format_for('ALG', ('R\n').encode()))
            #             else:
            #                 print(Fore.LIGHTBLUE_EX + '[Debug] Message from STM: %s' % str(messages))

            # except Exception as e:
            #     print(Fore.RED + '[MultiProcess-READ-STM ERROR] %s' % str(e))
            #     break

                message = self.STM.STM_connection.read(1).strip().decode() 

                if message is None:
                    continue
                print(Fore.LIGHTCYAN_EX + "STM Message received " + message)
                if len(message) != 0:
                        print(Fore.LIGHTRED_EX + 'STM > ALG | %s' % (str(message)))
                        self.message_queue.put_nowait(self._format_for('ALG', ('R').encode()))
                        print(Fore.LIGHTBLUE_EX + '[Debug] Message from STM: %s' % str(message))
                        self.lock = True
                # print("slowing down for 3 seconds")
                # time.sleep(3)
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

                        self.STM.write_to_STM(payload)
                        print(Fore.LIGHTCYAN_EX + 'To STM: after write to STM method')
                        # time.sleep(3)
                        # message = self.STM.read_from_STM()
                        # if message is None:
                        #         continue
                        # message = message.strip().decode() 
                        # print(Fore.LIGHTCYAN_EX + '[_write_target()] Message recvd and decoded as',str(message)) 
                        # if 'R' in message: 
                        #     print(Fore.LIGHTRED_EX + 'STM > %s , %s' % ('ALG', 'R'))
                        #     continue
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

                        # adding the stop preview and close above to avoid OutofResources MMAL error
                        self.camera.stop_preview()
                        self.camera.close()

                        #Reply received from the Image Processing Server
                        self.reply = self.sender.send_image(self.rpi_name, self.image)
                        self.reply = str(self.reply.decode())
                        print(Fore.LIGHTYELLOW_EX + 'Reply message: ' + self.reply)

                        # #Messages sent to ALG & AND')
                        # if self.reply == 'n':
                        #     self.reply = 'n'
                        #     self.message_queue.put_nowait(self._format_for('ALG',(self.reply).encode()))
                        #     print(Fore.LIGHTYELLOW_EX + 'Message send across to ALG: ' + self.reply)
                            
                        # else:
                        #     #msg format to AND: IMG-OBSTACLE_ID-IMG_ID e.g. "IMG-2-31"
                        print(self.obslst)
                        if len(self.obslst)>0:
                            message_obst = self.obslst[0]+self.reply
                            self.obslst.pop(0)
                            print(message_obst)
                            self.message_queue.put_nowait(self._format_for('AND',message_obst.encode()))
                            print(Fore.LIGHTYELLOW_EX + 'Message send across to AND: ' + message_obst)

                
                except Exception as e:
                    print(Fore.RED + '[MultiProcess-PROCESS-IMG ERROR] %s' % str(e))

