# import the necessary packages
from imutils.video import VideoStream
from picamera import PiCamera
from picamera.array import PiRGBArray
import imagezmq
import argparse
import socket
import time
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
	help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())
# initialize the ImageSender object with the socket address of the
# server
sender = imagezmq.ImageSender(connect_to="tcp://{}:50000".format(
	args["server_ip"]))


# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()
print(rpiName,"\t: the name of rpi")
# #connect to PiCamera and take capture from there
# vs = VideoStream(usePiCamera=True, resolution=(320, 240)).start() #choose resolution 
# #vs = VideoStream(src=0).start()
# time.sleep(2.0)
 
# while True:
# 	# read the frame from the camera and send it to the server
# 	frame = vs.read()
# 	sender.send_image(rpiName, frame)
while True: 
	option = input("Take picture:\t")
	if option == "y":
		camera = PiCamera(resolution=(640, 640))
		rawCapture = PiRGBArray(camera)
        print(rawCapture)
		camera.capture(rawCapture, format="bgr")
		image = rawCapture.array
        print(image)
		rawCapture.truncate(0)
		sender.send_image(rpiName, image)
							