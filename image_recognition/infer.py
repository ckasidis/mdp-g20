from loader import *

def run_inference(model, fixed_image, class_dictionary=desc_dict, debug=False):

  results = model(fixed_image)
  lst_id, lst_conf = [],[]
  df = results.pandas().xyxy[0]
  for i in df['name']: 
    lst_id.append(i)
  for j in df['confidence']: 
    lst_conf.append(j)

  if len(lst_id)>1 or len(lst_conf)>1: #multiple identified
    #find the biggest area
    print("(note: multiple objects were identified \ndifferentiating on the basis of area..)")
    df['area'] = (df['xmax']-df['xmin']) * (df['ymax']-df['ymin'])
    col='area'
    max_area_item = df.loc[df[col].idxmax()]
    lst_id, lst_conf =[],[]
    lst_id.append(max_area_item['name'])
    lst_conf.append(max_area_item['confidence'])

  try:
    cid = int(lst_id[0])
    conf = round(lst_conf[0]*100, 2)

    cid_desc = class_dictionary[str(cid)]


    results.render()
    results.crop()
    
    if debug==True:
      print(df)
      print("\n\nLabel found :\t",cid)
      print("Confidence :\t", conf, "%")
      print("Checking the description from dictionary, if applicable..")
      print(class_dictionary.get(str(cid), "Not found. Please check the image"))

      print("Result Image saved at ./images_debug")
      plt.imshow(np.squeeze(results.render()))
      plt.savefig("images_debug/results.png")
      print("Cropped Result Image saved at ./images_debug")
      plt.imshow(np.squeeze(results.crop()))
      plt.savefig("images_debug/results_crop.png")

    return cid, cid_desc, conf

  except:
    print("Unable to find object. Something's wrong")
    return None, None, None