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
from colorama import *
init(autoreset=True)


def draw_bbox(frame, info):
    try:
        print(Fore.WHITE + "[IMGREC] Drawing bounding box given the information...")
        for box in info: 
            if box[5]==0:
                xB = int(box[2])
                xA = int(box[0])
                yB = int(box[3])
                yA = int(box[1])
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
                cv2.imshow("OutputWindow",frame)
                cv2.imwrite("clean_frame.jpg", frame)
                print(Fore.GREEN+"[IMGREC] Saved boundingbox'd image at ./clean_frame.jpg ...")
    except Exception as e:
        print(Fore.RED + "[IMGREC] Draw-BoundingBox function error")

def load_model():
    print(Fore.LIGHTCYAN_EX+"[IMGREC] Setting up the Image Recognition system...")    
    print(Fore.LIGHTCYAN_EX+"[IMGREC] Loading model...")

    # model =  torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True) 
    model_path = r'C:\Users\siddh\Desktop\mdp-g20\image_recognition\yolov5\content\yolov5' # local
    wts_path = r'C:\Users\siddh\Desktop\mdp-g20\image_recognition\best-model.pt'

    model = torch.hub.load(model_path, 'custom', path=wts_path, source='local')  # local repo
    print(Fore.LIGHTCYAN_EX + "[IMGREC] Model loaded, trying to use GPU")
    
    try:
        model.to(torch.device("cuda:0"))
        print(Fore.GREEN +"[IMGREC] Model loaded to CUDA")
    except Exception as e:
        print(Fore.RED +"[IMGREC] Loading model to CUDA failed...\nUsing CPU")
        model.to(torch.device("cpu"))
        print(Fore.GREEN +"[IMGREC] Loaded into CPU memory")

    model.conf = 0.25  # confidence threshold (0-1)
    # model.iou = 0.45  # NMS IoU threshold (0-1)
    model.classes = [0] # (optional list) filter by class, i.e. = [0, 15, 16] for persons, cats and dogs


    print(Fore.GREEN +"[IMGREC] YOLOv5 Model initialisation done...")

    return model

def init():
    model = load_model()
    visited=[]
    # initialize the ImageHub object
    imageHub = imagezmq.ImageHub(open_port='tcp://192.168.20.25:5555')
    print(Fore.GREEN +"[IMGREC] ZMQ port for connection has been opened...")

    while True:
        # receive RPi name and frame from the RPi and acknowledge the receipt
        print(Fore.LIGHTCYAN_EX+"[IMGREC] Attempting to connect to Raspberry Pi")
        (rpiName, frame) = imageHub.recv_image()
        print(Fore.GREEN+"[IMGREC] Connection successful!")
        print(Fore.GREEN+"[IMGREC] Connected to", rpiName)
        
        # lastActive[rpiName] = datetime.now()
        resized = cv2.resize(frame,(640,640))
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB )
        (h, w) = resized.shape[:2]
        cv2.imwrite('frame.png', resized)

        print(Fore.LIGHTBLUE_EX+"[IMGREC] Running custom trained YOLOv5 model...")
        results = model(resized)
        print(Fore.LIGHTCYAN_EX+"[IMGREC] The results of Image Recognition are as follows:")
        
        info = results.pandas().xyxy[0].to_dict(orient = "records")
        print(info)
        
        if len(info) != 0:
            name = info[0]['name']
            confidence = info[0]['confidence']
            
            if confidence > 0.1: 
                encoded_name = str(name).encode()    
                print(Fore.WHITE+"[IMGREC] Object found, details are as follows:\nClass ID\t:{}\nConfidence\t:{}".format(name, confidence))
                f = open('ObjectIDsequence.json')
                # returns JSON object as 
                # a dictionary
                data = json.load(f)
                print(data)
                cid = data[0]
                i=0
                while True:
                    if cid not in visited:
                        cid = data[i]
                        visited.append(cid)
                        cid+='-'+name
                        imageHub.send_reply(cid)
                        break
                    elif cid in visited:
                        i+=1
                # imageHub.send_reply(encoded_name)
                print(Fore.GREEN+"[IMGREC] Message sent to RPi{}".format(cid))
                print(Fore.GREEN+"[IMGREC] Class ID {} sent to Raspberry Pi...".format(name))
    
                results.render()
                draw_bbox(frame, info)
                    
                print(Fore.WHITE+"[IMGREC] Rendered results have been saved in ./runs/detect/...")
                
                results.save()
                stitchImages.stitching()
                
                print(Fore.GREEN+"[IMGREC] Stitching of images is being done....")
            else:
                print(Fore.RED+"[IMGREC] Object was found but did not pass the minimum confidence threshold unfortuantely.") 
                imageHub.send_reply(b'n')
                print(Fore.RED+"[IMGREC] Sent null response to Raspberry Pi...")
                results.render()
                results.show()
                # results.save()


        else:
            print(Fore.WHITE+"[IMGREC] No object was found in the given image...")
            imageHub.send_reply(b'n') # no object found
            print(Fore.RED+"[IMGREC] Sent null response to Raspberry Pi...")
            results.render()
            results.show()
            # results.save()


if __name__ == "__main__":
    init()