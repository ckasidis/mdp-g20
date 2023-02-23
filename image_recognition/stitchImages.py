from imutils import paths
from PIL import Image
import cv2


def stitching():
  image_folder = r'C:\Users\siddh\Desktop\mdp-g20\image_recognition\runs\detect'
  #image_folder = r'./runs/detect'
  imagePaths = []
  # for directory in image_folder: 
  #       imagePaths.append(paths.list_images(directory))
  imagePaths = list(paths.list_images(image_folder))
  print(imagePaths)
  images = [Image.open(x) for x in imagePaths]
  widths, heights = zip(*(i.size for i in images))

  total_width = sum(widths)
  max_height = max(heights)

  new_im = Image.new('RGB', (total_width, max_height))

  x_offset = 0
  for im in images:
    new_im.paste(im, (x_offset,0))
    x_offset += im.size[0]

  new_im.save(r'C:\Users\siddh\Desktop\mdp-g20\image_recognition\runs\stitched\stitchedOutput.png', format='png')
  