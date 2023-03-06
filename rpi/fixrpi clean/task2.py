# Main script For Week 9 Task 

import time
import base64, os, glob, socket

from interface.STM32 import STM32
# from interface.Android import Android
from task2.task2_path import *
from task2.task2_utils import readMsg, takePic, process_image, readSTM

img_directory = "/home/pi/rpi/picamera_images/"
image_processing_server_url = "tcp://192.168.20.25:5555"
image_count = 0 # keep track of the images detected


if __name__ == '__main__':

    print("[MAIN] Initialising Multiprocessing Communication ...")

    # List of Interfaces - STM32F board, Android
    interfaces = []
    interfaces.append(STM32())

    # Index of the interfaces in the list
    STM = 0
    # ANDROID = 1

    # Establish connections between RPi and all other interfaces
    for interface in interfaces:
        interface.connect()

    print("[MAIN] Multiprocess communication started.")

    # Set up PiCamera
    print("[MAIN] Setting up PiCamera...")
    camera = PiCamera()
    print("[MAIN] PiCamera ready.")


    
    try: 
        print("[MAIN]: Heading to 1st obstacle.")
        for i in p_s:
            content = i[3:]
            interfaces[STM].write(content)
            readSTM(content)
        # Taking pic for 1st obstacle
        image = takePic()
        result_msg = process_image("1", image)
        print(result_msg)

        print("[MAIN]: Heading to 2nd obstacle.")
        if "right" in result_msg:
            r1 = "right"
            for i in p_r:
                content = i[3:]
                interfaces[STM].write(content)
                readSTM(content)
        else:
            for i in p_l:
                content = i[3:]
                interfaces[STM].write(content)
                readSTM(content)
        # Taking pic for 2nd obstacle
        image = takePic()
        result_msg = process_image("2", image)
        print(result_msg)

        print("[MAIN]: Heading back to carpark.")
        if "right" in result_msg:
            if r1 == "right":
                for i in p_rr:
                    content = i[3:]
                    interfaces[STM].write(content)
                    readSTM(content)
            else:
                for i in p_lr:
                    content = i[3:]
                    interfaces[STM].write(content)
                    readSTM(content)
        else:
            if r1 == "right":
                for i in p_rl:
                    content = i[3:]
                    interfaces[STM].write(content)
                    readSTM(content)
            else:
                for i in p_ll:
                    content = i[3:]
                    interfaces[STM].write(content)
                    readSTM(content)

        image = takePic()
        result_msg = process_image(image)

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        for i in interfaces:
            i.disconnect()
        camera.close()

    finally:
        for i in interfaces:
            i.disconnect()
        camera.close()
        print("[MAIN] Camera closed.")








