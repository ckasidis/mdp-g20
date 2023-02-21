# Standard library imports
import numpy as np
import json

# Custom imports
from algorithm_utils import main

def testAlgorithm():
    filename1 = 'AcquirefromAndroid.json'
    filename2 = 'commands2stm.json'
    commands = main(map_dir=filename1, cmd_dir=filename2) # Execute the main function and store cmds
    # print(commands)
    for i in commands:
        if i=='Camera':
            print("\nRPI|"+i)
        else:
            print("\nSTM|"+i)

def runAlgorithm():
    try:
        # Create a client to send and receive information from the RPi
        client = Client("192.168.20.1", 3004)  # 10.27.146 139 | 192.168.13.1
        client.connect()
        print("Algorithm PC successfully connected to Raspberry Pi")
    except Exception as e:
        print("[ALG-CONNECTION ERROR]",str(e))

    filename1 = 'mapFromAndroid.json'
    filename2 = 'commands2stm.json'
    stopword_from_STM = 'ALG|CMPLT'

    while True:
        try:
            print("\n===========================Receive Obstacles Data===========================\n")
            print("Waiting to receive obstacle data from ANDROID...")
            
            obstacle_data = client.receive() # Receive the obstacle data
            data2 = obstacle_data.decode() # Parse data from binary to JSON

            print("Received all obstacles data from ANDROID.")
            print(f"Obstacles data: {data2}")
            
            with open(filename1, "w") as f: # Store the data in a json file
                json.dump(data2, f, indent=4)

            print("\n===============================Calculate path===============================\n")
            commands = main(map_dir=filename1, cmd_dir=filename2) # Execute the main function and store cmds

            print("\nFull list of paths commands till last obstacle:")
            print(f"{commands}") # View the commands/actions generated

            print("\n\n=======================Send path commands to move to obstacles=======================\n")
            

            for command in commands: # IF SENDING ONE BY ONE
                command = 'STM|'+command
                print(f"\nSending path commands to execute the command {command} to RPI to STM...")
                client.send(command)

                print("\nWaiting to receive aknowledgement/image_id from STM/IMAGE REC")
                var = client.receive()
                print(f"Message received from STM(via RPi): {var}")

                if var == stopword_from_STM:
                    continue
                else:
                    print("Received a strange message from RPi, please cross-check.")

            
            '''
            # IF SENDING THE ENTIRE ARRAY AT ONCE
            arr_str = ','.join(str(x) for x in arr) # Converting the array to a string
            client.sendall(arr_str.encode()) # Sending the data
            print("Sent the commands (as an array) to RPi")
            '''

        except exception as e:
            print('[MAIN CONNECT FUNCTION ERROR]',str(e))

# Run the system
if __name__ =='__main__':
    # runAlgorithm()
    testAlgorithm()