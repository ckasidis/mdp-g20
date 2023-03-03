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

model_path = 'C:/Users/siddh/Desktop/mdp-g20/image_recognition/yolov5/content/yolov5' # local
wts_path = 'C:/Users/siddh/Desktop/mdp-g20/image_recognition/best-model.pt'
model = torch.hub.load(model_path, 'custom', path=wts_path, source='local')  # local repo
print("Model loaded")

# imageHub = imagezmq.ImageHub(open_port='tcp://192.168.20.25:5555')
imageHub = imagezmq.ImageHub()
print("ZMQ port for connection has been opened")

ESTIMATED_NUM_PIS = 1
ACTIVE_CHECK_PERIOD = 10
ACTIVE_CHECK_SECONDS = ACTIVE_CHECK_PERIOD * ESTIMATED_NUM_PIS

while True:
    (rpiName, frame) = imageHub.recv_image()
    print(rpiName, "connected")
    resized = cv2.resize(frame,(640,640))
    resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    (h, w) = resized.shape[:2]

    results = model(resized)   
    print(results)     
    info = results.pandas().xyxy[0].to_dict(orient = "records")
    results.render()
    results.show()
    if len(info) != 0:
        name = info[0]['name']
        confidence = info[0]['confidence']
            
        if confidence > 0.05: 
            # encoded_name = str(name).encode()    
            print("Object found, details are as follows:\nClass ID :\t{}\nConfidence :\t{}".format(name, confidence))
            imageHub.send_reply(str(name).encode())
            print("[IMGREC] Class ID {} sent to Raspberry Pi".format(name))
            # results.render()
            results.save()
            # results.show()
            stitchImages.stitching()
        else:
            imageHub.send_reply(b'n')
            # results.render()
            # results.show()
            results.save()

    else:
        imageHub.send_reply(b'n') # no object found
        # results.render()
        # results.show()
        results.save()

