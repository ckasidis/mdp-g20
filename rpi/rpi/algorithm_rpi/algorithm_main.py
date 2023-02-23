# Standard library imports
import numpy as np
import json

# Custom imports
from algorithm_utils import main, fixCommands
from re import M
import socket
import json


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
        print("=================================Connection=================================")
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

def testAlgorithm():

    ''' Obselete function'''
    filename1 = 'AcquirefromAndroid.json'
    filename2 = 'commands2stm.json'
    try:
        commands = main(map_dir=filename1, cmd_dir=filename2) # Execute the main function and store cmds
        for i in commands:
            if i=='Camera':
                print("\nRPI|"+i)
            else:
                print("\nSTM|"+i)
    # print(commands)
    except:
        print(Fore.RED + '[ALGO ERROR]')
    

def runAlgorithm():
    try:
        # Create a client to send and receive information from the RPi
        client = Client("192.168.20.1", 3004)  # 10.27.146 139 | 192.168.13.1
        client.connect()
        print(Fore.LIGHTGREEN_EX + "Algorithm PC successfully connected to Raspberry Pi...")

    except Exception as e:
        print(Fore.RED + "[ALG-CONNECTION ERROR]",str(e))

    filename1 = 'mapFromAndroid.json'
    filename2 = 'commands2stm.json'
    stopword_from_STM = 'CMPLT'

    while True:
        try:
            print("\n===========================Receive Obstacles Data===========================\n")
            print("Waiting to receive obstacle data from ANDROID...")
            
            obstacle_data = client.receive() # Receive the obstacle data
            data2 = obstacle_data # Parse data from binary to JSON

            print(Fore.LIGHTGREEN_EX + "Received all obstacles data from ANDROID.")
            print(Fore.LIGHTCYAN_EX + f"Obstacles data: {data2}")
            
            with open(filename1, "w") as f: # Store the data in a json file
                json.dump(data2, f, indent=4)

            print("\n===============================Calculate path===============================\n")
            print(Fore.LIGHTCYAN_EX + "Running the algorithm....")
            commands = main(map_dir=filename1, cmd_dir=filename2) # Execute the main function and store cmds
            print(Fore.LIGHTGREEN_EX + "The algorithm has completed computation, generating STM commands...")
            commands = fixCommands(commands)
            print("\nFull list of STM commands till last obstacle:")
            print(f'{commands}') # View the commands/actions generated

            print("\n\n=======================Send path commands to move to obstacles=======================\n")
            
            count=0
            for command in commands: # IF SENDING ONE BY ONE
                count+=1
                print(f"\nSending path commands to execute the command #{count} to RPI to STM...")
                client.send(command)

                print("Waiting to receive aknowledgement")
                var = client.receive()
                # print(f"Message received (via RPi): {var}")

                if var == stopword_from_STM:
                    print(Fore.LIGHTGREEN_EX + f"Acknowledgement received successfully, sending next command {command}...")
                    continue
                else:
                    print(Fore.RED + "Received a strange message from RPi, please cross-check.")
            
            # client.close()
            # break
            
            '''
            # IF SENDING THE ENTIRE ARRAY AT ONCE
            arr_str = ','.join(str(x) for x in arr) # Converting the array to a string
            client.sendall(arr_str.encode()) # Sending the data
            print("Sent the commands (as an array) to RPi")
            '''

        except KeyboardInterrupt:
            client.close()
            break

        except Exception as e:
            print(Fore.RED + '[MAIN CONNECT FUNCTION ERROR]',str(e))
            client.close()
            break

    # client.close()

# Run the system
if __name__ =='__main__':
    # runAlgorithm()
    testAlgorithm()