#!/usr/bin/env python
# coding: utf-8

import serial
import time
import subprocess


# Create a serial class
class sr_conn(object):

    def __init__(self):
        # Set the baud rate and the port number according to the port connected on the RPi
        self.port = '/dev/ttyUSB0'
        self.baud_rate = 115200
        self.service = None
        self.sr_conn_flag = False

    # Initialize serial connection
    def init_sr_conn(self):
        try:
            self.service = serial.Serial(self.port, self.baud_rate)
            time.sleep(2)
            self.sr_conn_flag = True
            print ("Created serial connection")

        except Exception as e:
            print ('ERROR init_sr_conn', str(e))

    def check_sr_conn(self):
        return self.sr_conn_flag

    def close_serial_conn(self):
        try:
            if (self.service):
                self.service.close()

            self.sr_conn_flag = False
            print ("Closed SR connection")

        except Exception as e:
            print('ERROR SR close connection', str(e))

    def write_to_serial(self, msg):
        try:
            self.service.write(msg)
            print ("\nwrote to SR", msg)

        except Exception as e:
            print ("ERROR SR write message", str(e))
            self.close_serial_conn()
            self.init_serial_conn()

    # Read the data from serial port
    def read_from_serial(self):
        try:
            received_data = self.service.readline()
            if received_data != b'':
                print ("\nread from SR", received_data)

            return received_data

        except Exception as e:
            print ("ERROR SR read message", str(e))
            self.close_serial_conn()
            self.init_sr_conn()