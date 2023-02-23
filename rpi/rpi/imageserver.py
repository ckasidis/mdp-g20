print("[IMGREC] Setting up the Image Recognition system...")
# import the necessary packages
from imutils import build_montages
from datetime import datetime
import numpy as np
import imagezmq
import argparse
import imutils
import cv2
import torch
import stitchImages
import time

st = time.time()

# initialize the ImageHub object
imageHub = imagezmq.ImageHub(open_port='tcp://192.168.20.25:5555')
# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class

# load our serialized model from disk
print("[IMGREC] Loading model...")

#change path accordingly
#model =  torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True) 

#run locally 
model = torch.hub.load(r'C:\Users\siddh\Desktop\Projects\rpi-imgrec\yolov5\content\yolov5', 'custom', path=r'C:\Users\siddh\Desktop\Projects\rpi-imgrec\best-model.pt', source='local')  # local repo

print("[IMGREC] YOLOv5 Model initialisation done...")

# initialize the consider set (class labels we care about and want
# to count), the object count dictionary, and the frame  dictionary
CONSIDER = set(["dog", "person", "car"])
objCount = {obj: 0 for obj in CONSIDER}
frameDict = {}
# initialize the dictionary which will contain  information regarding
# when a device was last active, then store the last time the check
# was made was now
lastActive = {}
lastActiveCheck = datetime.now()
# stores the estimated number of Pis, active checking period, and
# calculates the duration seconds to wait before making a check to
# see if a device was active
ESTIMATED_NUM_PIS = 1
ACTIVE_CHECK_PERIOD = 10
ACTIVE_CHECK_SECONDS = ESTIMATED_NUM_PIS * ACTIVE_CHECK_PERIOD

# print("it works till here.")
# start looping over all the frames
print("[IMGREC] The initialisation of parameters is done...")
while True:
    # receive RPi name and frame from the RPi and acknowledge
	# the receipt
    print("[IMGREC] Attempting to connect to Raspberry Pi")
    (rpiName, frame) = imageHub.recv_image()
    print("[IMGREC] Connection successful!")
    print("[IMGREC] Connected to", rpiName)
	# if a device is not in the last active dictionary then it means
	# that its a newly connected device
    if rpiName not in lastActive.keys():
        print("[IMGREC] Receiving data from {}...".format(rpiName))
	# record the last active time for the device from which we just
	# received a frame
    
    lastActive[rpiName] = datetime.now()
    #frame = imutils.resize(frame, width=640)
    resized = cv2.resize(frame,(640,640))
    (h, w) = resized.shape[:2]

    #frame = imutils.resize(frame, width=400)
    #set confidence for model 
    # model.conf = 0.85
    print("[IMGREC] Running custom trained YOLOv5 model...")
    results = model(resized)
    print("[IMGREC] The results of Image Recognition are as follows:")
    print(results)
    info = results.pandas().xyxy[0].to_dict(orient = "records")
    if len(info) != 0:
        #id = info[0]['class']
        name = info[0]['name']
        confidence = info[0]['confidence']
        if confidence > 0.3: 
            #encoded_id = str(id).encode()
            # name = "AND|"+name
            encoded_name = str(name).encode()
            print("[IMGREC] Object found, details are as follows:\nClass ID\t:{}\nConfidence\t:{}".format(name, confidence))
            imageHub.send_reply(encoded_name)
            print("[IMGREC] Class ID {} sent to Raspberry Pi...".format(name))
            results.render()
            results.show()
            print("[IMGREC] Rendered results have been saved in ./runs/detect/...")
            results.save()
            stitchImages.stitching()
            print("[IMGREC] Stitching of images is being done....")
            # img = cv2.imread('runs/stitched/stitchedOutput.png')
            # img_resize = cv2.resize(img, (960,540))
            # cv2.imshow('Stitched Image', img_resize)
        else:
            print("[IMGREC] Object was found but did not pass the minimum confidence threshold unfortuantely.") 
            imageHub.send_reply(b'n')
            print("[IMGREC] Sent null response to Raspberry Pi...")
            # results.render()
            # results.show()
            # results.save()



    else:
        print("[IMGREC] No object was found in the given image...")
        imageHub.send_reply(b'n') # no object found
        print("[IMGREC] Sent null response to Raspberry Pi...")
        # results.render()
        # results.show()
        # results.save()

    print("[IMGREC] Time taken for inference and set up is \t: {} seconds...".format((time.time()-st)))