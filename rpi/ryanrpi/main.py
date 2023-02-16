from Rpi_MultiProcess import MultiProcess
import time
import serial
#import sys
from colorama import *

init(autoreset=True)
#print(sys.version)
#print(sys.path)
def init():
    try:
        multi = MultiProcess()
        multi.start()
    except KeyboardInterrupt:
        multi.AND.disconnect_AND()
        multi.ALG.disconnect_ALG()
        multi.STM.disconnect_STM() 
    except Exception as err:
        print(Fore.RED + '[Main.py ERROR] {}'.format(str(err)))
        multi.AND.disconnect_AND()
        multi.ALG.disconnect_ALG()
        multi.STM.disconnect_STM()

if __name__ == '__main__':
    init()
