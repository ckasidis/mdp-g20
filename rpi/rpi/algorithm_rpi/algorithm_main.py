# Standard library imports
import numpy as np
import json

# Custom imports
from algorithm_utils import main, fixCommands
from re import M
import socket
import json
import algotest

from colorama import *
init(autoreset=True)
# print(sys.version)
# print(sys.path)


class Client:
    """
    Used as the client for RPI.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket()
    
    def connect(self):
        print("Connection")
        print(f"Attempting connection to ALGO at {self.host}:{self.port}")
        self.socket.connect((self.host, self.port))
        print(Fore.LIGHTGREEN_EX + "Connected to ALGO!")

    def send(self, d):
        data = d.encode()
        self.socket.send(data)

    def receive(self):
        msg = self.socket.recv(1024)
        data = msg.decode()
        return(data)

    def is_json(self, msg):
        try:
            data = json.loads(msg)
            d = data["obstacle1"]
            return data
        except Exception:
            print(Fore.RED + "Exception occured")
            return False

    def close(self):
        print(Fore.LIGHTCYAN_EX + "Closing client socket.")
        self.socket.close()


def runAlgorithm():
    try:
        client = Client("192.168.20.1", 3004) 
        client.connect()
        print(Fore.LIGHTGREEN_EX + "Algorithm PC successfully connected to Raspberry Pi...")

    except Exception as e:
        print(Fore.RED + "[ALG-CONNECTION ERROR]",str(e))

    filename1 = 'mapFromAndroid.json'
    filename2 = 'commands2stm.json'
    stopword_from_STM = 'CMPLT'

    while True:
        try:
            print("\nReceive Obstacles Data\n")
            print("Waiting to receive obstacle data from ANDROID...")
            
            obstacle_data = client.receive() # Receive the obstacle data
            data2 = obstacle_data # Parse data from binary to JSON

            print(Fore.LIGHTGREEN_EX + "Received all obstacles data from ANDROID.")
            print(Fore.LIGHTCYAN_EX + f"Obstacles data: {data2}")
            
            with open(filename1, "w") as f: # Store the data in a json file
                json.dump(data2, f, indent=4)

            commands, obsOrder = RunMain(map_dir=filename1, cmd_dir=filename2) # Execute the main function and store cmds
            # commands = fixCommands(commands)
            print("\nFull list of STM commands till last obstacle:")
            print(f'{commands}') # View the commands/actions generated
            print(f'The order of visiting obstacles is:\n',obsOrder)
            all_cmd_str = ','.join(str(e) for e in commands)
            all_obs_str = ','.join(str(e) for e in obsOrder)
            all_str = all_cmd + "$" + all_obs_str
            client.send(all_str)
            # print("Sent path commands to RPi\n")
            # client.send(all_obs_str)
            # print("Sent obstacles order to RPi")
            client.close()
            # break
            

        except KeyboardInterrupt:
            client.close()
            break

        except Exception as e:
            print(Fore.RED + '[MAIN CONNECT FUNCTION ERROR]',str(e))
            client.close()
            break

# Run the system
if __name__ =='__main__':
    runAlgorithm()
