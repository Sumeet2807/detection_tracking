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
import os
import pickle
import threading
import copy
import boto3
import botocore


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
           

def save_data(out, data, dest=0):   

    file_name = "hm_" + str(time.time()) + ".pkl"
    file_path = out + "/" + file_name
    with open(file_path, "wb") as f:
        pickle.dump(data,f)

    if int(dest) == 1:
        aws_s3 = boto3.resource('s3')
        s3 = boto3.client('s3')
        s3.upload_file(file_path,"axelta-production",file_name)
        print("file uploaded")
        object_acl = aws_s3.ObjectAcl("axelta-production",file_name)
        response = object_acl.put(ACL='public-read')
        



# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--source", type=int, default=1, help="1 for video; 2 for webcam")
ap.add_argument("-v", "--video", default=None, help="path to the video file")
ap.add_argument("-d", "--destination", type=int, default=0, help="0 for file; 1 for amazon S3 as well")
ap.add_argument("-o", "--output", default="output", help="path to the output folder")
ap.add_argument("-fs", "--frameskip", type=int, default=1, help="every fth frame should be processed")
ap.add_argument("-fr", "--framerate", type=int, default=30, help="camera framerate")
ap.add_argument("-t", "--time", type=int, default=0, help="output files to be generated appx t minutes")
# ap.add_argument("-a", "--min-area", type=int, default=250, help="minimum area size")
args = vars(ap.parse_args())
if args["source"] == 1 and args["video"] == None:
	ap.error("video needs to be supplied in video mode")

if args["source"] == 1:
    vs = cv2.VideoCapture(args["video"])  
    framerate = int((vs.get(cv2.CAP_PROP_FPS)))

elif args["source"] == 2:
	vs = cv2.VideoCapture(0)
	framerate = args["framerate"] 	
else:    
    exit()    

fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

time_out = int(args["time"])
save_count = framerate * 60 * time_out

firstFrame = None
frame_count = 0

frameskip = int(args["frameskip"])
if frameskip < 1:
    frameskip = 1


t1_init = 0
t2_init = 0

#out_subdir = args["output"] + "/" + str(time.time()) + "_" + str(time_out)
# if os.path.isdir(out_subdir) is False:
#     os.mkdir(out_subdir)


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

    if  time_out > 0:
        if frame_count % save_count == 0:
            accum_image = accum_image1 + accum_image2
            save_data(args["output"], (firstFrame,accum_image), args["destination"])



if time_out == 0:
    accum_image = accum_image1 + accum_image2
    save_data(args["output"], (firstFrame,accum_image), args["destination"])


vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
