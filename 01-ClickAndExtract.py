#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2  # BGR, np.array
import csv
import os
import sys
import pandas as pd
import numpy as np
import glob              # glob file name list
import Functions as fun
import importlib
importlib.reload(fun)

# For every image in dir_img there must be one in dir_mask (with same name)
dir_img   = '/home/jrmgarcia/ProjData/OilDSs/OilSpillDetection/train/images/'
dir_mask  = '/home/jrmgarcia/ProjData/OilDSs/OilSpillDetection/train/labels/'

# OpenCV is BGR, PIL is RGB, mpl is RGB
cor1 = tuple([0,255,255])
cor2 = tuple([0,255,0])
cor3 = tuple([255,0,0])
R=0; G=1; B=2
H=0; S=1; I=2

args = sys.argv[1:]
scr_wid, scr_hei = fun.getLargerMonitor()
thickness=1
rect_col = [255, 255, 255]  
  
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


# Callback function for mouse interation over the image, captures clicks
# Think that when this method is executed, the window with 3 imgs is already been shown
def click_and_do(event, x, y, flags, param):
   # grab references to the global variables
   global img_work  # allows changing global var
   
   # if the left mouse button was clicked, record the starting
   # (x, y) coordinates and indicate that clipping is being performed
   
   if event == cv2.EVENT_LBUTTONDOWN:
      print(x, y, x1_ok, x2_ok)
      if x < x1_ok or x > x2_ok:
         return
      sel_mask = img_show[y, x] # cyan

      mask = cv2.inRange(img_label, sel_mask, sel_mask)
      indices = np.where(mask !=0 )  
      # len(indices[0]), len(indices[1]), img.shape, img.shape[0]*img.shape[1]
      img_work = img.copy()
      img_work[indices[0], indices[1], :] = [255, 255, 0]
      #cv2.imshow("work", img_work)
      #key = cv2.waitKey(0) & 0xFF
      #cv2.destroyAllWindows()
 
   # elif event == cv2.EVENT_MOUSEMOVE:
   #    img_work = img.copy()  # works over a copy of the original and intact image
   #    # draws all already registered rectangles around the regions of interest (ROI)
   #    # the current one will be draw below
   #    for r in range(0, len(refPt)):
   #       rect_col = cor1 if refPt[r][2] == 1 else cor2 if refPt[r][2] == 2 else cor3
   #       cv2.rectangle(img_work, refPt[r][0], refPt[r][1], rect_col, thickness)
   #    cv2.imshow("img_work", img_work)
      
   #    if clipping == True:
   #       # draw the rectangle that is being drawn
   #       rect_col = cor1 if bg_type == 1 else cor2 if bg_type == 2 else cor3
   #       cv2.rectangle(img_work, refPt_loc[0], (x,y), rect_col, thickness)
   #       cv2.imshow("img_work", img_work)
         
   if cross_on:
      cv2.line(img_work, (x, 0), (x, img_hei), rect_col, 1)
      cv2.line(img_work, (0, y), (img_wid, y), rect_col, 1)
      #cv2.imshow("img_work", img_work)

# Getting all fnames
fnames = sorted(glob.glob(dir_img + '/*.jpg'))
idx_img=0; fname_img = fnames[idx_img]
for idx_img, fname_img in enumerate(fnames):
   img_ori  = cv2.imread(fname_img)                      # ***** BGR FORMAT ******
   fname_label = fname_img.replace("images", "labels").replace("jpg", "png")
   img_ori    = cv2.imread(fname_img)                      # ***** BGR FORMAT ******
   img_label  = cv2.imread(fname_label)                    # ***** BGR FORMAT ******
   img_ori_hei, img_ori_wid, _ = img_ori.shape
   head, tail = os.path.split(fname_img)
   
   # Statistics stored in a file with the same basename of the original image file name
   fname_clip = f"./dataout/{tail.replace('jpg', 'csv')}"

   print("---------------------------------------------------------------------------")
   print("* Img fname: ", tail, ": ", sep="",)
   print("* Img dim..: ", img_ori_wid, "x", img_ori_hei, ", asp_ratio: ", img_ori_hei / img_ori_wid, ", resizing, ", sep="", end="", flush=True) 
   img, fac_wid, fac_hei = fun.resizeImg(img_ori, scr_wid, scr_hei)
   img_label, fac_wid, fac_hei = fun.resizeImg(img_label, scr_wid, scr_hei)
   img_work = img.copy()
   print("---------------------------------------------------------------------------")
   img1D = img.reshape(-1, 3) # 2D to 1D
   # img_ori.shape, img.shape, img_label.shape

   img_hei, img_wid, _ = img.shape
   #print("new img dim: ", img_wid, "x", img_hei, ",  fact wid: ", fac_wid, ",  fact hei: ", fac_hei, sep="", flush=True)

   # Use must click on the image at the center
   x1_ok = img.shape[1] + 1
   x2_ok = x1_ok + img.shape[1]

   #cv2.destroyAllWindows()
   # FLAGS: WINDOW_AUTOSIZE   --> Default, 
   #        WINDOW_GUI_NORMAL --> Disable right click menu (context menu)
   # Just create a named placeholder for the image, in order to assign a callback function to it
   # before its creation
   cv2.namedWindow("img_show")  # cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
   cv2.setMouseCallback("img_show", click_and_do)

   # initialize the list of reference points and boolean indicating
   # whether clipping is being performed or not
   refPt = refPt_loc = []
   clipping = False # true if mouse is pressed
   bg_type = 1  # starting with clear sky rectangles
   cross_on = True  # Controls show/no show of the cross while moving over the image

   print("\nControls:\nMouse down: select mask\nMouse up..: unselect\n\n(N) Next Image \
          \n(X) Extract masked info\n(+) Toggle cross on/off \n(Q) Quit\n")
   
   # keep looping until the 'q' key is pressed
   key=""
   while True:
      #msg("- Tipo de óleo ativo: " + ("SOBRE AREIA" if bg_type == 1 else "SOBRE OUTRA" if bg_type == 2 else "NÃO-ÓLEO"), 
      #    "i" if bg_type == 1 else "g" if bg_type == 2 else "x")
      
      # Draws all rectangles around the regions of interest (ROI)
      #for r in range(0, len(refPt)):
      #   rect_col = cor1 if refPt[r][2] == 1 else cor2 if refPt[r][2] == 2 else cor3
      #   cv2.rectangle(img_work, refPt[r][0], refPt[r][1], rect_col, thickness)
         
      # Concatenate the original, the labeled and the working (ori+label) images
      img_show = cv2.hconcat([img, img_label, img_work])
      # display the image and wait for a keypress
      cv2.imshow("img_show", img_show)
      #cv2.moveWindow("img_show", 100, 0)
      key = cv2.waitKey(0) & 0xFF
      cv2.destroyAllWindows()
      
      if key == ord("d"):      # delete last clipped region
         img_work = img.copy()
         if len(refPt) > 0:
           refPt.pop()
      elif key == ord("1"):    # set óleo na areia
         bg_type = 1
      elif key == ord("2"):    # set óleo em outra superfície
         bg_type = 2
      elif key == ord("3"):    # registro de não óleo (em qq superfície)
         bg_type = 3
      elif key == ord("+"):    # toggle crossed lines on/off
         cross_on = not cross_on
      elif key == ord("n"):    # next image
         break
      elif key == ord("q"):    # quit
         break

      # Move the file to the ignore directory in order to be ignored in the next file listing
      # If one want to consider it again one must put it back in the "dir_img" directory manually
      #if key == ord("i"):    
      #   fname_2ignore = f"{dir_2ignore}{tail}"
      #   os.replace(fname_img, fname_2ignore)
      #   print("* Image:", fname_2ignore, "moved to", dir_2ignore, flush=True)
      #   break
  
      # Registra      
      if (len(refPt) > 0) and (key == ord("r") or key == ord("o")):
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

