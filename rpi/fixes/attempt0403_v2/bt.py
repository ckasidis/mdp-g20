#!/usr/bin/env python
# coding: utf-8

from bluetooth import *


class bt_conn(object):

    def __init__(self):

        self.server_socket = None
        self.client_socket = None
        self.bt_conn_flag = False

    def close_bt_conn(self):

        try:
            if self.client_socket:
                self.client_socket.close()
            if self.server_socket:
                self.server_socket.close()
            self.bt_conn_flag = False
            print("Closed BT connection")
        except Exception as e:
            print('ERROR BT close connection')

    def bt_check_conn_status(self):
        return self.bt_conn_flag

    def init_bt_conn(self):
        while True:
            # Creating the server socket and bind to port
            btport = 1
            retry = False
            try:
                self.server_socket = BluetoothSocket(RFCOMM)
                self.server_socket.bind(("", btport))
                self.server_socket.listen(1)
                self.port = self.server_socket.getsockname()[1]
                uuid = "621de399-020a-4ee8-bac5-b656c5d53abb"

                advertise_service(self.server_socket, "SampleServer",
                                  service_id=uuid,
                                  service_classes=[uuid, SERIAL_PORT_CLASS],
                                  profiles=[SERIAL_PORT_PROFILE],
                                  )
                print("Waiting for BT connection on rfcomm channel %d" % self.port)
                
                self.client_socket, client_address = self.server_socket.accept()
                print("Created BT connection with ", client_address)
                self.bt_conn_flag = True
                retry = False

            except Exception as e:
                print('ERROR init_bt_conn', str(e))
                retry = True
            if not retry:
                break

    def write_to_bt(self, message):
        try:
            self.client_socket.send(message)
            print("\nwrote to BT")

        except BluetoothError:
            print("\nBluetooth Error. Connection lost")
            self.close_bt_conn()
            self.init_bt_conn()

        except Exception as e:
            print("ERROR BT write message", str(e))

    def read_from_bt(self):
        try:
            msg = self.client_socket.recv(2048)
            if msg!=b'':
                print('\nread from BT', msg)
            return msg

        except BluetoothError:
            print("\nBluetooth Error. Connection lost")
            self.close_bt_conn()
            self.init_bt_conn()

        except Exception as e:
            print("ERROR BT read message", str(e))