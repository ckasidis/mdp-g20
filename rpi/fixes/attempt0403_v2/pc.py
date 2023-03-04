#!/usr/bin/env python
# coding: utf-8

import socket
import sys
import time 


class pc_conn:

    # connect from PC to RPi on the port 1334. IP is '' as it accepts all incoming connections
    def __init__(self):
        self.ip = '192.168.18.18'
        self.port = 5454
        self.conn = None
        self.client = None
        self.addr = None
        self.pc_conn_flag = False

    # Bind the IP to the port and listen for client connection
    def init_pc_conn(self):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print('PC Socket created at', self.ip)

            self.conn.bind((self.ip, self.port))
            print ('Waiting for client connection')

            self.conn.listen(5)
            self.client, self.addr = self.conn.accept()
            print('Created PC connection with client')

            self.pc_conn_flag = True

        except Exception as e:
            print('ERROR init_pc_conn', str(e))

    def close_conn(self):
        try:
            if self.conn:
                self.conn.close()

            if self.client:
                self.client.close()

            self.pc_conn_flag = False
            print('Closed PC Connection')

        except Exception as e:
            print('ERROR PC close connection', str(e))

    def check_conn_status(self):
        return self.pc_conn_flag

    def write_to_pc(self, message):
        try:
            self.client.sendto(message, self.addr)
            print("\nwrote to PC", message)

        except Exception as e:
            print("ERROR PC write message", str(e))

    def read_from_pc(self):
        try:
            recv_data = self.client.recv(2048)  # size of data which can be received
            if recv_data != b'':
                print('\nread from PC', recv_data)

            return recv_data

        except Exception as e:
            print('ERROR PC read message', str(e))