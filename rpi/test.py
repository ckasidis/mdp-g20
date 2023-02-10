import os
import argparse

def init():

    os.system("sudo hciconfig hci0 piscan")

if __name__ == '__main__':
    init()
