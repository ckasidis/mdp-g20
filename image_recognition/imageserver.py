from datetime import datetime

import cv2
import imagezmq
import imutils
import numpy as np
import stitchImages
import torch
from env import ACTIVE_CHECK_SECONDS, model_path, wts_path
from imutils import build_montages

model = torch.hub.load(model_path, 'custom', path=wts_path, source='local')  # local repo
print("Model loaded")

# imageHub = imagezmq.ImageHub(open_port='tcp://192.168.20.25:5555')
imageHub = imagezmq.ImageHub()
print("ZMQ port for connection has been opened")

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
            print("\n\nObject found, details are as follows:\nClass ID :\t{}\nConfidence :\t{}\n\n".format(name, confidence))
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