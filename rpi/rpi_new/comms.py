### Outline for Task 1 ###
from comms_utils import *

### Main Loop ### 
if __name__ == '__main__':

    ### Make all the connections ###
    and_server, and_client = connect2Android() # Connect to Android Tablet (via BT)
    alg_connect, alg_client = connect2AlgorithmPC() # Connect to Image Server PC (via WiFi)
    ir_sender, camera, rpi_name = connect2IR() # Connect to Image Server PC (via WiFi)
    stm_connection = connect2STM() # Connect to STM (via USB)

    ### Compute Path and Commands ###
    sendPath2Alg(and_client, alg_client)

    recvAllCmdsfromALG()

    ### Main loop ###
    # while True:
        # if Command == 'RPI|TOCAM':
    #       RASPBERRY PI <--takePic => takePicRPi()
    #       RASPBERRY PI --sendImage-> IMG REC PC => sendPic2IR()
    #       IMG REC PC <--runInference-- => runYOLOv5()
    #       IMG REC PC --sendClassID-> RASPBERRY PI => sendID2RPi()
    #       RASPBERRY PI --sendClassID_AND-> ANDROID => sendID2AND()
#   else:
#       RASPBERRY PI --SendCommand()-> STM => sendCmd2STM()
#       STM --sendACK()-> RASPBERRY PI => recvACKfromSTM()
#   elif command == 'RPI_END|0':
#       RASPBERRY PI --closeConnection()-> STM  => closeSTMcomm()
#       RASPBERRY PI --closeConnection()-> ANDROID  => closeANDcomms()
#       RASPBERRY PI --closeConnection()-> ALGORITHM PC  => closeALGOcomms()
#       RASPBERRY PI --closeConnection()-> IMG REC PC  => closeIRcomms()
#       break