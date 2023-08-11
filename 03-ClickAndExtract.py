#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2  # BGR, np.array
import csv
import os
import sys
import pandas as pd
import numpy as np
import glob              # glob file name list
import Functions as Fun
import Fun_Stat as FunStat
import importlib
importlib.reload(Fun)
importlib.reload(FunStat)

# For every image in dir_img there must be one in dir_mask (with same name)
dir_img   = '/home/jrmgarcia/ProjData/OilDSs/OilSpillDetection/train/images'
dir_mask  = '/home/jrmgarcia/ProjData/OilDSs/OilSpillDetection/train/labels'

# Remember: OpenCV is BGR, PIL is RGB, mpl is RGB
scr_wid, scr_hei = Fun.getLargerMonitor()
  
def msg(text, msg_type="y"):
   ESC = "\x1B["
   if msg_type == "y":             # ok 
      print(ESC + "30;42m" + text) 
   elif msg_type == "i":           # info
      print(ESC + "97;44m" + text)   
   elif msg_type == "n":           # alert
      print(ESC + "97;41m" + text)   
   elif msg_type == "x":           # não-óleo
      print(ESC + "48;5;196m" + text)   
   else:
      print(ESC + "97;100m" + text) # grey bg 
      
   print(ESC + "0m")  # RESET ALL ATTRIBS


# Callback function for mouse interation over the image, captures clicks and movements
# Think that when this method is executed, the window with 3 imgs is already been shown
def click_and_do(event, x, y, flags, param):
   # grab references to the global variables
   global sel_mask, img_work, img_show, indexes  # allows changing global var
   
   # if left mouse button was clicked ...
   if event == cv2.EVENT_LBUTTONDOWN:
      # User must click on img_label (the one in the middle) only
      if x < img.shape[1] or x > img.shape[1] * 2:
         return
      # x=1183; y=158
      sel_mask = img_show[y, x]
      print(f"CLICKED ON x={x}, y={y}, sel_mask={sel_mask}")
      img_work = img.copy()
      mask = cv2.inRange(img_label, sel_mask, sel_mask)
      indexes = np.where(mask != 0)  
      # len(indexes[0]), len(indexes[1]), img.shape, img.shape[0]*img.shape[1]
      img_work[indexes[0], indexes[1], :] = sel_mask
      img_show = cv2.hconcat([img, img_label, img_work])
      cv2.imshow("img_show", img_show) # Shows the new image over the old one
      #key = cv2.waitKey(0) & 0xFF
      #cv2.destroyAllWindows()

# Getting all fnames
fnames = sorted(glob.glob(dir_img + '/*.jpg'))
idx_img=0; fname_img = fnames[idx_img]
for idx_img, fname_img in enumerate(fnames):
   img_ori  = cv2.imread(fname_img)                       # ***** BGR FORMAT ******
   fname_label = fname_img.replace("images", "labels").replace("jpg", "png")
   img_label  = cv2.imread(fname_label)                    # ***** BGR FORMAT ******
   img_ori_hei, img_ori_wid, _ = img_ori.shape
   head, tail = os.path.split(fname_img)
   
   # Statistics stored in a file with the same basename of the original image file name
   fname_stat = f"./3-stats/stat_{tail.replace('jpg', 'csv')}"

   print("---------------------------------------------------------------------------")
   print("* Img fname: ", tail, ": ", sep="",)
   print("* Img dim..: ", img_ori_wid, "x", img_ori_hei, ", asp_ratio: ", img_ori_hei / img_ori_wid, ", resizing, ", sep="", end="", flush=True) 
   
   # Resize the images to fit 3 of them, side by side
   img, fac_wid, fac_hei = Fun.resizeImg(img_ori, scr_wid, scr_hei)
   img_label, fac_wid, fac_hei = Fun.resizeImg(img_label, scr_wid, scr_hei)
   img_work = img.copy()
   img.shape, img_label.shape, img_work.shape
   assert img.shape == img_label.shape == img_work.shape

   print("---------------------------------------------------------------------------")
   img_hei, img_wid, _ = img.shape
   indexes = None

   # Creating a named placeholder for the image that will suffer mouse movements consequences
   # in order to assign a callback function to it before the creation of the window itself
   cv2.namedWindow("img_show")
   cv2.setMouseCallback("img_show", click_and_do)

   print("\nControls:\nMouse down: select mask\n(N) Next Image \
          \n(X) Extract masked info\n(Q) Quit\n")

   # keep looping until the 'q' key is pressed
   key=""
   while True:
      # Concatenate 3 images horizontally
      img_show = cv2.hconcat([img, img_label, img_work])
      cv2.imshow("img_show", img_show)
      key = cv2.waitKey(0) & 0xFF

      if key == ord("x"):    # toggle crossed lines on/off
         print("Extracting statistics:")
      elif key == ord("n"):    # next image
         break
      elif key == ord("q"):    # quit
         break
      # Extract 
      if (indexes is not None) and (key == ord("x")):
         data = img[indexes[0], indexes[1], 0]  # all color dimension are iqual, only one is needed
         print(FunStat.get_stats(data))


      #    dsRGB_image = pd.DataFrame(columns=col_names)  # DS dos quadrantes de uma imagem
      #    #fname_clip = dir_clipped + re.sub("jpg|jpeg", "csv", tail, flags=re.I)

      #    # Remove se já existir         
      #    if os.path.isfile(fname_clip):
      #       os.remove(fname_clip)
            
      #    for r in range(len(refPt)):
      #       # retorna os pontos para a imagem original 
      #       x1 = min(refPt[r][0][0], refPt[r][1][0])
      #       x2 = max(refPt[r][0][0], refPt[r][1][0])
      #       y1 = min(refPt[r][0][1], refPt[r][1][1])
      #       y2 = max(refPt[r][0][1], refPt[r][1][1])
      #       print("* Image limits after resized (x1,x2,y1,y2): ", x1, x2, y1, y2, flush=True)

      #       # Torna o retangulo sendo analisado com as bordas vermelhas
      #       img_work2 = img_work.copy()  
      #       cv2.rectangle(img=img_work2, pt1=(x1, y1), pt2=(x2, y2), color=tuple([0,0,255]))#, thickness=cv2.FILLED)
      #       cv2.imshow("img_work", img_work2)
            
      #       x1 = int(x1 * fac_wid)
      #       x2 = int(x2 * fac_wid)
      #       y1 = int(y1 * fac_hei)
      #       y2 = int(y2 * fac_hei)
      #       print("* Corresponding original image limits (x1,x2,y1,y2): ", x1, x2, y1, y2, flush=True)

      #       bg_type_str = "AREIA" if refPt[r][2] == 1 else "OUTRO" if refPt[r][2] == 2 else "NAO_OLEO"
            
      #       # Mostra o quadrante sendo registrado
      #       clip = img_ori[y1:(y2+1), x1:(x2+1)]     # Todos os pixels do quadrante em formato 2D da imagem intacta
      #       #clip = fun.zoomclip(rect2D, 200)
      #       cv2.imshow("clip", clip)            
      #       cv2.waitKey(0) & 0xFF
      #       cv2.destroyWindow("clip")

      #       new_row = [bg_type_str, x1, x2, y1, y2]
      #       # rewrite the file
      #       with open(fname_clip, 'a') as f:
      #          writer = csv.writer(f, delimiter=";")
      #          writer.writerow(new_row)               
               
      #       msg("- Clipped region REGISTERED: " + str(x1) + " to " + str(x2) + " and " + str(y1) + " to " + str(y2), "i")

         if key == ord("o"):    # register and leave
            break

   # Leave image iteration
   if key == ord("q") or key == ord("t"):    # next image
      break
        
   # close all cv2 windows
   cv2.destroyAllWindows()    

