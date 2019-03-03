# USAGE
# python multi_cam_motion.py

# import the necessary packages
from __future__ import print_function
from imutils.video import VideoStream
import argparse
from datetime import datetime as dt
import imutils
import time
import cv2
import numpy as np
import pickle
import threading
import copy


def frame_proc(var,frame):
    global accum_image2
    global accum_image1
    frame = imutils.resize(frame, width=500)
    (height, width) = frame.shape[:2]

       
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    fgmask = fgbg.apply(gray)  # remove the background
    thresh = 2
    maxValue = 2
    ret, th1 = cv2.threshold(fgmask, thresh, maxValue, cv2.THRESH_BINARY)
    if var != 1:
        accum_image2 = np.add(accum_image2, th1)
    else:
        accum_image1 = np.add(accum_image1, th1)
           





# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="path to the video file")
ap.add_argument("-o", "--output", default="out.pyd", help="path to the output file")
ap.add_argument("-f", "--frameskip", default=1, help="every fth frame should be processed")
# ap.add_argument("-a", "--min-area", type=int, default=250, help="minimum area size")
args = vars(ap.parse_args())


vs = cv2.VideoCapture(args["video"])  
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

firstFrame = None
frame_count = 0

frameskip = int(args["frameskip"])
if frameskip < 1:
    frameskip = 1

t1_init = 0
t2_init = 0

while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    ret, frame = vs.read()   
    if frame is None:
        break

    frame_count += 1

    if frame_count % frameskip != 0 and frame_count != 1:
        continue
    if frame_count == 1:

        frame = imutils.resize(frame, width=500)
        (height, width) = frame.shape[:2]

        firstFrame = copy.deepcopy(frame)       
        accum_image1 = np.zeros((height, width))
        accum_image2 = np.zeros((height, width))
        continue
   
    if t1_init == 0:
        t1 = threading.Thread(target=frame_proc, args=(1,frame))
        t1.start()
        last_thread = 1
        t1_init = 1
        continue

    if t2_init == 0:
        t2 = threading.Thread(target=frame_proc, args=(2,frame))
        t2.start()
        last_thread = 2
        t2_init = 1
        continue


    
    if t1.isAlive():
        if t2.isAlive():
            if last_thread == 1:
                t2.join()
                t2 = threading.Thread(target=frame_proc, args=(2,frame))
                t2.start()
                last_thread = 2
            else:
                t1.join()
                t1 = threading.Thread(target=frame_proc, args=(1,frame))
                t1.start()
                last_thread = 1
        else:
            t2 = threading.Thread(target=frame_proc, args=(2,frame))
            t2.start()
            last_thread = 2
    else:
        t1 = threading.Thread(target=frame_proc, args=(1,frame))
        t1.start()
        last_thread = 1

accum_image = accum_image1 + accum_image2   
with open(args["output"], "wb") as f:
    pickle.dump((firstFrame,accum_image),f)

vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
