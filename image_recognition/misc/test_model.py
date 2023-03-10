# import the necessary packages

import cv2
import torch

model_path = 'C:/Users/siddh/Desktop/mdp-g20/image_recognition/yolov5/content/yolov5' # local
wts_path = 'C:/Users/siddh/Desktop/mdp-g20/image_recognition/best-model.pt'
model = torch.hub.load(model_path, 'custom', path=wts_path, source='local', verbose=False)  # local repo
model.to(torch.device(0))
print("Model loaded")

img = cv2.imread('image2.jpg')
resized = cv2.resize(img,(640,640))

resized = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# (h, w) = resized.shape[:2]

results = model(resized)
info = results.pandas().xyxy[0].to_dict(orient = "records")
results.render()
results.show()
