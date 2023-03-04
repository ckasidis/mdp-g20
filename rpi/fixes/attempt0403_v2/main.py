import sys
import time
import picamera
from multiprocessing import Queue
import threading

from pc import *
from bt import *
from sr import *
from img import *

import os
from os.path import join
import numpy as np
import struct


class Main(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.bt_thread = bt_conn()
        self.pc_thread = pc_conn()
        self.sr_thread = sr_conn()
        self.im_thread = im_conn()
        
        print('CONNECT TO BT')
        self.bt_thread.init_bt_conn()
        print('CONNECT TO PC')
        self.pc_thread.init_pc_conn()
        print('CONNECT TO SR')
        self.sr_thread.init_sr_conn()
        print('CONNECT TO IMG')
        self.im_thread.init_im_conn()

        time.sleep(1)

    # PC Functions #
    def writePC(self, msg_to_pc):
        if self.pc_thread.check_conn_status() and msg_to_pc:
            self.pc_thread.write_to_pc(msg_to_pc.encode())
            print ("Message sent to [PC]: %s" % msg_to_pc)
            return True

        return False 

    def readPC(self):
        while True:
            read_pc_msg = self.pc_thread.read_from_pc()
            if read_pc_msg!=None:

                read_pc_msg = read_pc_msg.decode("utf-8")
                pc_msgs = read_pc_msg.split('Q')
                for read_pc_msg in pc_msgs:

                    if read_pc_msg == "":
                        continue

                    if self.pc_thread.check_conn_status() and read_pc_msg:

                        # PC to Android
                        if (read_pc_msg[0:2].lower() == 'an'):
                            print ("Message from [PC] --> [ANDROID]: %s" % read_pc_msg[2:])
                            pc_msgSent = self.writeBT(read_pc_msg[2:])

                            if (read_pc_msg[2:4].lower()=='md'):
                                img_coor = read_pc_msg[2:].split(' ')
                                img_coor = '_' + str(img_coor[2]) + '_' + str(img_coor[3]) + '_' + str(img_coor[4])
                                print ("Message from [PC] --> [IMAGE]: %s" % img_coor)            
                                im_msgSent = self.writeIM(img_coor)

                            elif (read_pc_msg[2:].lower()=='end'):
                                im_msgSent = self.writeIM('end')

                        # PC to Arduino
                        elif (read_pc_msg[0:2].lower() == 'ar'):
                            print ("Message from [PC] --> [ROBOT]: %s" % read_pc_msg[2:])
                            pc_msgSent = self.writeSR(read_pc_msg[2:])
                            
                        else:
                            print ("\nIncorrect header from PC, ", read_pc_msg)

    # Android/BT functions #
    def writeBT(self, msg_to_bt):
        if self.bt_thread.bt_check_conn_status() and msg_to_bt:
            if type(msg_to_bt) is bytes:
                self.bt_thread.write_to_bt(msg_to_bt)
                print('Message sent to [ANDROID]: image data')
            else:
                self.bt_thread.write_to_bt(msg_to_bt.encode())
                print ("Message sent to [ANDROID]: %s" % msg_to_bt)
            return True

        return False

    def readBT(self):
        while True:
            read_bt_msg = self.bt_thread.read_from_bt()
            if read_bt_msg!=None:

                read_bt_msg = read_bt_msg.decode("utf-8")
                bt_msgs = read_bt_msg.split('Q')
                for read_bt_msg in bt_msgs:
                    
                    if read_bt_msg == "":
                        continue

                    if self.bt_thread.bt_check_conn_status() and read_bt_msg:
                        
                        # Android to PC
                        if (read_bt_msg[0:2].lower() == 'pc'):
                            print ("Message from [ANDROID] --> [PC]: %s" % read_bt_msg[2:])
                            bt_msgSent = self.writePC(read_bt_msg[2:]+'\n')

                        # Android to Arduino
                        elif (read_bt_msg[0:2].lower() == 'ar'):
                            print ("Message from [ANDROID] --> [ROBOT]: %s" % read_bt_msg[2:])
                            bt_msgSent = self.writeSR(read_bt_msg[2:])
                            
                        else:
                            print ("\nIncorrect header from BT, ", read_bt_msg)

    # Serial Comm functions #
    def writeSR(self, msg_to_sr):
        if self.sr_thread.check_sr_conn() and msg_to_sr:
            self.sr_thread.write_to_serial(msg_to_sr.encode())
            print ("Message sent to [ROBOT]: %s" % msg_to_sr)
            return True
        return False

    def readSR(self):
        while True:
            read_sr_msg = self.sr_thread.read_from_serial()
            if read_sr_msg != None:
                read_sr_msg = read_sr_msg.decode("utf-8")
                sr_msgs = read_sr_msg.split('Q')
                for read_sr_msg in sr_msgs:
                    
                    if read_sr_msg == "":
                        continue
                    
                    if self.sr_thread.check_sr_conn() and read_sr_msg:
                        # Robot to PC #
                        if (read_sr_msg[0:2].lower() == 'pc'):
                            print ("Message from [ROBOT] --> [PC]: %s" % read_sr_msg[2:] + "|")
                            sr_msgSent = self.writePC(read_sr_msg[2:])
                            
                        # Robot to Android
                        elif (read_sr_msg[0:2].lower() == 'an'):
                            print ("Message from [ROBOT] --> [ANDROID]: %s" % read_sr_msg[2:])
                            self.writeBT(read_sr_msg[2:])


                        else:
                            print ("\nIncorrect header from SR, ", read_sr_msg)
                            pass

    # Image Comm functions #
    def writeIM(self, img_coor):
        if self.im_thread.check_conn_status() and img_coor:
            self.im_thread.write_image(img_coor.encode())
            print ("Message sent to [IMG]: %s" % img_coor)
            return True

        return False

    def readIM(self):
        while True:
            read_im_msg = self.im_thread.read_image()
            if read_im_msg != None and read_im_msg!=b"":
                if self.im_thread.check_conn_status():
                    # IMG to Android
                    print ("Message from [IMG] --> [ANDROID]: %s" % read_im_msg)
                    im_msgSent = self.writeBT(read_im_msg)

    def initialize_threads(self):
        # PC read and write thread
        readt_pc = threading.Thread(target=self.readPC, name="pc_read_thread")
        writet_pc = threading.Thread(target=self.writePC, args=("",), name="pc_write_thread")
        print('PC thread created')
        
        # Bluetooth (BT) read and write thread
        readt_bt = threading.Thread(target=self.readBT, name="bt_read_thread")
        writet_bt = threading.Thread(target=self.writeBT, args=("",), name="bt_write_thread")
        print('BT thread created')

        # Serial (SR) read and write thread

        readt_sr = threading.Thread(target=self.readSR, name="sr_read_thread")
        writet_sr = threading.Thread(target=self.writeSR, args=("",), name="sr_write_thread")
        print('SR thread created')

        # Image (IMG) read and write thread
        readt_im = threading.Thread(target=self.readIM, name="im_read_thread")
        writet_im = threading.Thread(target=self.writeIM, args=("",), name="im_write_thread")
        print('IMG thread created')

        # Set threads as daemons
        readt_pc.daemon = True
        writet_pc.daemon = True
        readt_bt.daemon = True
        writet_bt.daemon = True
        readt_sr.daemon = True
        writet_sr.daemon = True
        readt_im.daemon = True
        writet_im.daemon = True

        # Start Threads
        readt_pc.start()
        writet_pc.start()
        readt_bt.start()
        writet_bt.start()
        readt_sr.start()
        writet_sr.start()
        readt_im.start()
        writet_im.start()
        print ("All threads initialized successfully")

    def initialize_pc_thread(self):
        readt_pc = threading.Thread(target=self.readPC, name="pc_read_thread")
        writet_pc = threading.Thread(target=self.writePC, args=("",), name="pc_write_thread")
        print('PC thread created')
        readt_pc.daemon = True
        writet_pc.daemon = True
        readt_pc.start()
        writet_pc.start()


    def initialize_bt_thread(self):
        readt_bt = threading.Thread(target=self.readBT, name="bt_read_thread")
        writet_bt = threading.Thread(target=self.writeBT, args=("",), name="bt_write_thread")
        print('BT thread created')
        readt_bt.daemon = True
        writet_bt.daemon = True
        readt_bt.start()
        writet_bt.start()


    def initialize_sr_thread(self):
        readt_sr = threading.Thread(target=self.readSR, name="sr_read_thread")
        writet_sr = threading.Thread(target=self.writeSR, args=("",), name="sr_write_thread")
        print('SR thread created')
        readt_sr.daemon = True
        writet_sr.daemon = True
        readt_sr.start()
        writet_sr.start()

        
    def close_all_sockets(self):
        self.pc_thread.close_conn()
        self.bt_thread.close_bt_conn()
        self.sr_thread.close_serial_conn()
        self.sr_thread.close_im_conn()
        print ("Ended all threads")

    def keep_main_alive(self):
        while True:
            time.sleep(1)


if __name__ == '__main__':
    conn_obj = Main()
    conn_obj.initialize_threads()
    conn_obj.keep_main_alive()
    conn_obj.close_all_sockets()