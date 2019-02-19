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
import numpy as np


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
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


hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

initBB = None

# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])

# initialize the FPS throughput estimator
first_frame = 1
tracker_lost = 1
fps = None
frame_number = 0
wait_time = 250
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

		(rects, weights) = hog.detectMultiScale(frame, winStride=(4, 4),padding=(8, 8), scale=1.05)
		rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
		pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)		
		if len(pick) > 0:l
			print(pick[0])
			xa, ya, xb, yb = pick[0]  
			initBB = (xa, ya, xb-xa, yb-ya)
			tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
			tracker.init(frame, initBB)	
			fps = FPS().start()
		
		

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
		
		# update the FPS counter
		fps.update()
		fps.stop()

		# initialize the set of information we'll be displaying on
		# the frame
		info = [
		 	("Tracker", args["tracker"]),
		 	("Success", "Yes" if success else "No"),
		 	("FPS", "{:.2f}".format(fps.fps())),
		 ]

		# # loop over the info tuples and draw them on our frame
		for (i, (k, v)) in enumerate(info):
		 	text = "{}: {}".format(k, v)
		 	cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
		 		cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 's' key is selected, we are going to "select" a bounding
	# box to track
	if key == ord("s"):
		# select the bounding box of the object we want to track (make
		# sure you press ENTER or SPACE after selecting the ROI)
		initBB = cv2.selectROI("Frame", frame, fromCenter=False,
			showCrosshair=True)

		# start OpenCV object tracker using the supplied bounding box
		# coordinates, then start the FPS throughput estimator as well
		tracker.init(frame, initBB)
		fps = FPS().start()

	# if the `q` key was pressed, break from the loop
	elif key == ord("q"):
		break

# if we are using a webcam, release the pointer
if not args.get("video", False):
	vs.stop()

# otherwise, release the file pointer
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()