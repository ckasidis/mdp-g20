import torch
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt

desc_dict={"11":"one","12":"two","13":"three","14":"four","15":"five",
                  "16":"six","17":"seven","18":"eight","19":"nine",
                  "20":"Alphabet A","21":"Alphabet B","22":"Alphabet C",
                  "23":"Alphabet D","24":"Alphabet E","25":"Alphabet F",
                  "26":"Alphabet G","27":"Alphabet H","28":"Alphabet S",
                  "29":"Alphabet T","30":"Alphabet U","31":"Alphabet V",
                  "32":"Alphabet W","33":"Alphabet X","34":"Alphabet Y","35":"Alphabet Z",
                  "36":"Up arrow","37":"down arrow","38":"right arrow",
                  "39":"left arrow","40":"Stop"
                  }


def load_model(weights_pt = 'pretrained_mdp_weights.pt'):
  model = torch.hub.load('ultralytics/yolov5', 'custom', 
                         path='runs/train/yolov5_TL5/weights/best.pt', 
                         _verbose=False,
                         force_reload=True,
                         source='github')
  model.verbose=False
  return model

def load_image(img_path, rotate=False, debug=False):
  original_image = Image.open(img_path)

  resized_image = original_image.resize((640, 640))

  #add logic to rotate only when original_image.shape[0]<original_image.shape[1]
  if rotate==True:
    angle = -90
    resized_and_rotated_image = resized_image.rotate(angle)
  else:
    angle=0
    resized_and_rotated_image = resized_image

  if debug==True:
    print("Original Image saved at ./images_debug")
    # %matplotlib inline
    # plt.imshow(np.squeeze(original_image))
    plt.savefig("images_debug/original_image.png")
    # cv2.imshow("original", original_image)
    
    print("Resized Image saved at ./images_debug")
    print(f"Original size \t: {original_image.size}")
    print(f"Resized to \t: {resized_image.size}")
    # %matplotlib inline
    plt.imshow(np.squeeze(resized_image))
    plt.savefig("images_debug/resized_image.png")
    # cv2.imshow("resized_image", resized_image)

    print("Rotated and Resized Image saved at ./images_debug")
    print("The image is being rotated counterclockwise by", str(angle))
    # %matplotlib inline
    plt.imshow(np.squeeze(resized_and_rotated_image))
    plt.savefig("images_debug/resized_and_rotated_image.png")
    # cv2.imshow("resized_and_rotated_image", resized_and_rotated_image)

  return np.asarray(resized_and_rotated_image)