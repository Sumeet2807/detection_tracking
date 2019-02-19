# USAGE
# python opencv_object_tracking.py
# python opencv_object_tracking.py --video dashcam_boston.mp4 --tracker csrt

# import the necessary packages

from __future__ import print_function
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
from imutils.object_detection import non_max_suppression
from imutils import paths
import detector_class as dc
import numpy as np


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
	help="path to input video file")
ap.add_argument("-d", "--detector", default="motion",type=str,
	help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
	help="OpenCV object tracker type")
args = vars(ap.parse_args())

# extract the OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]

# if we are using OpenCV 3.2 OR BEFORE, we can use a special factory
# function to create our object tracker
if int(major) == 3 and int(minor) < 3:
	tracker = cv2.Tracker_create(args["tracker"].upper())

# otherwise, for OpenCV 3.3 OR NEWER, we need to explicity call the
# approrpiate object tracker constructor:
else:
	# initialize a dictionary that maps strings to their corresponding
	# OpenCV object tracker implementations
	OPENCV_OBJECT_TRACKERS = {
		"csrt": cv2.TrackerCSRT_create,
		"kcf": cv2.TrackerKCF_create,
		"boosting": cv2.TrackerBoosting_create,
		"mil": cv2.TrackerMIL_create,
		"tld": cv2.TrackerTLD_create,
		"medianflow": cv2.TrackerMedianFlow_create,
		"mosse": cv2.TrackerMOSSE_create
	}

	# grab the appropriate object tracker using our dictionary of
	# OpenCV object tracker objects
	tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

# initialize the bounding box coordinates of the object we are going
# to track

detector = dc.detector_mul(args["detector"])

frame_number = 0
initBB = None

# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])


tracker_lost = 1
wait_time = 75
# loop over frames from the video stream
while True:
	
	# grab the current frame, then handle if we are using a
	# VideoStream or VideoCapture object
	frame = vs.read()
	frame = frame[1] if args.get("video", False) else frame

	# check to see if we have reached the end of the stream
	if frame is None:
		break
	frame_number += 1
	
        
	# resize the frame (so we can process it faster) and grab the
	# frame dimensions
	frame = imutils.resize(frame, width=500)
	(H, W) = frame.shape[:2]

	if frame_number % wait_time == 0 :#and tracker_lost == 1:
		wait_time = 50
		print("detecting")

		rects = detector.detect(frame)
		
		if len(rects) > 0:
			for (x,y,w,h) in rects:
				if w*h < (H*W/4) and w/h < 0.5 and w/h > 0.3 :					

					initBB = (x,y,w,h)
					tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
					tracker.init(frame, initBB)		
					break	
		

	# check to see if we are currently tracking an object
	if initBB is not None:
		# grab the new bounding box coordinates of the object
		(success, box) = tracker.update(frame)

		# check to see if the tracking was a success
		if success:
			tracker_lost = 0
			(x, y, w, h) = [int(v) for v in box]
			cv2.rectangle(frame, (x, y), (x + w, y + h),
				(0, 255, 0), 2)
			tracker_lost = 0
		else: 
			tracker_lost = 1
		

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	

# if we are using a webcam, release the pointer
if not args.get("video", False):
	vs.stop()

# otherwise, release the file pointer
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()