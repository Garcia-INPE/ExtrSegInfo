#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2  # BGR, np.array
import csv
import os
import sys
import numpy as np
import pandas as pd
from random import randint
import glob              # glob file name list
import Functions as fun

# OpenCV is BGR, PIL is RGB, mpl is RGB
cor1 = tuple([0,255,255])
cor2 = tuple([0,255,0])
cor3 = tuple([255,0,0])
R=0; G=1; B=2
H=0; S=1; I=2

args = sys.argv[1:]
out_dir = [i for i in args if "OUT_DIR" in i]
if len(out_dir) > 0: 
   out_dir = out_dir[0].split(sep="=")[1]
mon_res = [i for i in args if "MON_RES" in i]
if len(mon_res) > 0:
   mon_res = mon_res[0].split(sep="=")[1]
   
if len(mon_res)>0:
    scr_wid = mon_res.split(sep="x")[0]
    scr_hei = mon_res.split(sep="x")[1]
    print("informed: ", scr_wid, "x", scr_hei, sep="")
else:
    scr_wid, scr_hei = fun.getLargerMonitor()


thickness=1
#col_namesExpl = ["H","S","I","SD","VAR","LUM","W","W2","R_POW","G_POW","B_POW"]
#col_names = ["R","G","B","H","S","I","SD","VAR","LUM","W","W2","R_POW","G_POW","B_POW","AVG", "BG_TYPE"]
col_names = ["R", "G", "B", "H","S","I","SD","VAR","LUM","W","W2","R_POW","G_POW","B_POW","AVG", "BG_TYPE"]
  
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


# Callback function for mouse moviment over the image
# Capture a single over movement and clicks
def click_and_clip(event, x, y, flags, param):
   # grab references to the global variables
   global refPt, refPt_loc, clipping, img_work  # allows changing global var
   
   # if the left mouse button was clicked, record the starting
   # (x, y) coordinates and indicate that clipping is being performed
   # cv2 col = BGR
   # Blue line for óleo sobre areia and black line for sobre outra superfície
   rect_col = cor1 if bg_type == 1 else cor2 if bg_type == 2 else cor3
   
   if event == cv2.EVENT_LBUTTONDOWN:
      if not clipping:  # liga
          clipping = True
          refPt_loc = [(x,y)]
      else:             # desliga
          clipping = False
          # record the ending (x, y) coordinates and indicate that
          # the clipping operation is finished
          refPt_loc.append((x,y))
          refPt_loc.append(bg_type)
          refPt.append(refPt_loc)
          # draws all rectangles around the regions of interest (ROI)
          # "all" is because the last one has been done here
          for r in range(0, len(refPt)):
             rect_col = cor1 if refPt[r][2] == 1 else cor2 if refPt[r][2] == 2 else cor3
             cv2.rectangle(img_work, refPt[r][0], refPt[r][1], rect_col, thickness)
          cv2.imshow("img_work", img_work)

   elif event == cv2.EVENT_MOUSEMOVE:
      img_work = img.copy()  # works over a copy of the original and intact image
      # draws all already registered rectangles around the regions of interest (ROI)
      # the current one will be draw below
      for r in range(0, len(refPt)):
         rect_col = cor1 if refPt[r][2] == 1 else cor2 if refPt[r][2] == 2 else cor3
         cv2.rectangle(img_work, refPt[r][0], refPt[r][1], rect_col, thickness)
      cv2.imshow("img_work", img_work)
      
      if clipping == True:
         # draw the rectangle that is being drawn
         rect_col = cor1 if bg_type == 1 else cor2 if bg_type == 2 else cor3
         cv2.rectangle(img_work, refPt_loc[0], (x,y), rect_col, thickness)
         cv2.imshow("img_work", img_work)
         
   if cross_on:
      cv2.line(img_work, (x, 0), (x, img_hei), rect_col, 1)
      cv2.line(img_work, (0, y), (img_wid, y), rect_col, 1)
      cv2.imshow("img_work", img_work)

dir_img = "FotosIBAMA2019/"   # The image source directory must exist 
dir_clipped = "FotosIBAMA2019_clipped_csv/"
dir_2ignore = "FotosIBAMA2019_ignored_img/"

# Getting all fnames
fnames = [os.path.basename(x) for x in sorted(glob.glob(dir_img + '*.[j|J]*'))]

# Get the fnames of the already clipped images
if not os.path.exists(dir_clipped):
    os.mkdir(dir_clipped)

fnames_clipped = [os.path.basename(x) for x in sorted(glob.glob(dir_clipped + '*.csv'))]
fnames_clipped = [fn.replace(".csv", "") for fn in fnames_clipped]
#if len(fnames_clipped) > 0:
#   fnames_clipped = list(filter(lambda x: [fn for fn in fnames_clipped][0] in x, fnames))

# Get the fnames of images to be ignored
if not os.path.exists(dir_2ignore):
    os.mkdir(dir_2ignore)
fnames_2ignore = [os.path.basename(x) for x in sorted(glob.glob(dir_2ignore + '*.[j|J]*'))]

# Filters out already processed images out from the image list
fnames = sorted(list(set(fnames) - set(fnames_clipped) - set(fnames_2ignore)))

fname_img = fnames[0]
while True:
   idx_img = randint(0, len(fnames)-1)
   fname_img = dir_img + fnames[idx_img]
   #fname_img = "FotosIBAMA2019/15716599849656083154271581913798.jpg"
   img_ori  = cv2.imread(fname_img)                      # ***** BGR FORMAT ******
   img_ori_hei, img_ori_wid, _ = img_ori.shape
   head, tail = os.path.split(fname_img)
   fname_clip = f"{dir_clipped}{tail}.csv"  # Só acrescenta ".csv" ao final do nome da img
   print("\n---------------------------------------------------------------------------")
   print("* Img fname: ", tail, ": ", sep="",)
   print("* Img dim..: ", img_ori_wid, "x", img_ori_hei, ", asp_ratio: ", img_ori_hei / img_ori_wid, ", resizing, ", sep="", end="", flush=True) 
   img, fac_wid, fac_hei = fun.resizeImg(img_ori, scr_wid, scr_hei)
   #img, fac_wid, fac_hei = fun.resizeImg(img_ori, int(5120/2.5), int(2880/2.5)) # Mac retina Priscila
   print("---------------------------------------------------------------------------")
   img1D = img.reshape(-1, 3) # 2D to 1D

   img_hei, img_wid, _ = img.shape
   #print("new img dim: ", img_wid, "x", img_hei, ",  fact wid: ", fac_wid, ",  fact hei: ", fac_hei, sep="", flush=True)

   # Trabalhar retângulos em img_work e deixar img intacta para capturar os quadrantes
   img_work = img.copy()

   #cv2.destroyAllWindows()
   # FLAGS: WINDOW_AUTOSIZE --> Default, WINDOW_GUI_NORMAL --> Disable right click menu (context menu)
   # Usei WINDOW_GUI_NORMAL para permitir que o quadrante sendo marcado possa ser deslocado para um dos 4 lados (ao clicar)
   cv2.namedWindow("img_work") #, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
   cv2.setMouseCallback("img_work", click_and_clip)

   # initialize the list of reference points and boolean indicating
   # whether clipping is being performed or not
   refPt = refPt_loc = []
   clipping = False # true if mouse is pressed
   bg_type = 1  # starting with clear sky rectangles
   cross_on = True  # Controls show/no show of the cross while moving over the image

   print("\nControls:\nMouse down: region begin\nMouse up..: region end \n\n(D) Delete last clipping region \n(N) Next Image \
          \n(1) Óleo na areia \n(2) Óleo sobre outra superfície  \n(3) Não óleo \n(R) Register clip and continue in the same image\n(O) Register clip and load next image \
          \n(I) Mark image to be ignored \n(+) Toggle cross on/off \n(Q) Quit\n")
   
   # keep looping until the 'q' key is pressed
   key=""
   while True:
      msg("- Tipo de óleo ativo: " + ("SOBRE AREIA" if bg_type == 1 else "SOBRE OUTRA" if bg_type == 2 else "NÃO-ÓLEO"), 
          "i" if bg_type == 1 else "g" if bg_type == 2 else "x")
      
      # Draws all rectangles around the regions of interest (ROI)
      for r in range(0, len(refPt)):
         rect_col = cor1 if refPt[r][2] == 1 else cor2 if refPt[r][2] == 2 else cor3
         cv2.rectangle(img_work, refPt[r][0], refPt[r][1], rect_col, thickness)
         
      # display the image and wait for a keypress
      cv2.imshow("img_work", img_work)
      cv2.moveWindow("img_work", 100, 0)
      #plt.imshow(img_ori)
      key = cv2.waitKey(0) & 0xFF
      
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
      if key == ord("i"):    
         fname_2ignore = f"{dir_2ignore}{tail}"
         os.replace(fname_img, fname_2ignore)
         print("* Image:", fname_2ignore, "moved to", dir_2ignore, flush=True)
         break
  
      # Registra      
      if (len(refPt) > 0) and (key == ord("r") or key == ord("o")):
         dsRGB_image = pd.DataFrame(columns=col_names)  # DS dos quadrantes de uma imagem
         #fname_clip = dir_clipped + re.sub("jpg|jpeg", "csv", tail, flags=re.I)

         # Remove se já existir         
         if os.path.isfile(fname_clip):
            os.remove(fname_clip)
            
         for r in range(len(refPt)):
            # retorna os pontos para a imagem original 
            x1 = min(refPt[r][0][0], refPt[r][1][0])
            x2 = max(refPt[r][0][0], refPt[r][1][0])
            y1 = min(refPt[r][0][1], refPt[r][1][1])
            y2 = max(refPt[r][0][1], refPt[r][1][1])
            print("* Image limits after resized (x1,x2,y1,y2): ", x1, x2, y1, y2, flush=True)

            # Torna o retangulo sendo analisado com as bordas vermelhas
            img_work2 = img_work.copy()  
            cv2.rectangle(img=img_work2, pt1=(x1, y1), pt2=(x2, y2), color=tuple([0,0,255]))#, thickness=cv2.FILLED)
            cv2.imshow("img_work", img_work2)
            
            x1 = int(x1 * fac_wid)
            x2 = int(x2 * fac_wid)
            y1 = int(y1 * fac_hei)
            y2 = int(y2 * fac_hei)
            print("* Corresponding original image limits (x1,x2,y1,y2): ", x1, x2, y1, y2, flush=True)

            bg_type_str = "AREIA" if refPt[r][2] == 1 else "OUTRO" if refPt[r][2] == 2 else "NAO_OLEO"
            
            # Mostra o quadrante sendo registrado
            clip = img_ori[y1:(y2+1), x1:(x2+1)]     # Todos os pixels do quadrante em formato 2D da imagem intacta
            #clip = fun.zoomclip(rect2D, 200)
            cv2.imshow("clip", clip)            
            cv2.waitKey(0) & 0xFF
            cv2.destroyWindow("clip")

            new_row = [bg_type_str, x1, x2, y1, y2]
            # rewrite the file
            with open(fname_clip, 'a') as f:
               writer = csv.writer(f, delimiter=";")
               writer.writerow(new_row)               
               
            msg("- Clipped region REGISTERED: " + str(x1) + " to " + str(x2) + " and " + str(y1) + " to " + str(y2), "i")

         if key == ord("o"):    # register and leave
            break

   # Leave image iteration
   if key == ord("q") or key == ord("t"):    # next image
      break
        
   # close all cv2 windows
   cv2.destroyAllWindows()    

