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
import copy


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--frameskip", default=1, help="path to the video file")
# ap.add_argument("-a", "--min-area", type=int, default=250, help="minimum area size")
args = vars(ap.parse_args())

fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
# initialize the video streams and allow them to warmup
print("[INFO] starting cameras...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

time_prev = dt.now()    

firstFrame = None
frame_count = 0
frame_centroids = []

frameskip = int(args["frameskip"])
if frameskip < 1:
    frameskip = 1

while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    frame = vs.read()   
    if frame is None:
        break

    frame_count += 1

    if frame_count % frameskip != 0 and frame_count != 1:
        continue

    frame = imutils.resize(frame, width=500)
    (height, width) = frame.shape[:2]

    if frame_count == 1:

        firstFrame = copy.deepcopy(frame)       
        accum_image = np.zeros((height, width))
        continue

   
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    fgmask = fgbg.apply(gray)  # remove the background
    thresh = 2
    maxValue = 2
    ret, th1 = cv2.threshold(fgmask, thresh, maxValue, cv2.THRESH_BINARY)
           

            # add to the accumulated image
    
    accum_image = np.add(accum_image, th1)

    if frame_count % 3600 == 0:         

        
        with open("hm.pyd", "wb") as f:
            pickle.dump((firstFrame,accum_image),f)

  




vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
