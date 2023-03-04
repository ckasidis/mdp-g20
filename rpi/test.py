import os
import argparse

def init():

    os.system("sudo hciconfig hci0 piscan")


def move(ser, instr):
    bytesToRead = ser.inWaiting()
    while True:
        raw_dat = ser.read(1)
        dat = raw_dat.strip().decode('utf-8')
        print(instr, raw_dat)
        if dat=='R':
            break