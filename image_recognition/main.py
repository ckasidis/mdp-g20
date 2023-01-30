from loader import *
from infer import *
import argparse

#write a function for argument parser
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, 
                        default=r'runs\train\yolov5_TL5\weights\best.pt', 
                        help='custom weights path, default using pretrained weights for MDP')
    parser.add_argument('--image', type=str, default='', help='Image to run inference on', required=True)
    parser.add_argument('--rotate', type=bool, default=False, help='Rotate 90 deg anti clockwise')
    parser.add_argument('--debug', type=bool, default=False, help='Debug and see intermediate steps')

    return parser.parse_args()

if __name__ == '__main__':

    args = parse_args()

    PATH_TO_WT = args.weights
    PATH_TO_IMG = args.image
    _rotate = args.rotate
    _debug = args.debug

    _model = load_model(weights_pt = PATH_TO_WT)
    image = load_image(img_path = PATH_TO_IMG, rotate=_rotate, debug=_debug)
    cid, description, conf = run_inference(model=_model, fixed_image=image, debug=_debug)

    print("---"*15)
    print("Image inference using custom YOLOv5 done! \n\nHere are the results..")
    print("1.) Image ID\t:", cid)
    print("2.) Description\t:", description)
    print("3.) Probability\t:", conf,"%")
    print("---"*15)

    
# if cid is not None:
#   print("cid")