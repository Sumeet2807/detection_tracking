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


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=250, help="minimum area size")
args = vars(ap.parse_args())


# initialize the video streams and allow them to warmup
print("[INFO] starting cameras...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

time_prev = dt.now()	

firstFrame = None
frame_count = 0
frame_centroids = []

while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
	frame = vs.read()
	# frame = frame if args.get("video", None) is None else frame[1]
	

	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if frame is None:
		break

	frame_count += 1
	if frame_count % 4 != 0:
		continue

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	(H, W) = frame.shape[:2]
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
	

	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray
		continue

	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(firstFrame, gray)	
	if frame_count % 150 == 0:
		if cv2.sumElems(frameDelta)[0] < 100000:
			firstFrame = gray
			continue

	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	centroids = []

	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		c_x = int(((2*x)+w)/2)
		c_y = int(((2*y)+h)/2)

		frame_centroids.append([frame_count,c_x, c_y])
	

	#frame_centroids.append([frame_count, centroids])
	if frame_count % 3600 == 0:
		time_now = dt.now()
		file_name = str(time_prev) + "__" + str(time_now) + ".pyd"
		time_prev = time_now
		with open(file_name, "wb") as f:
			pickle.dump(frame_centroids,f)

		frame_centroids = []




vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
# # loop over frames from the video streams
# while True:
# 	# initialize the list of frames that have been processed
# 	frames = []

# 	# loop over the frames and their respective motion detectors
	
# 		# read the next frame from the video stream and resize
# 		# it to have a maximum width of 400 pixels
# 	frame = webcam.read()
# 	frame = imutils.resize(frame, width=400)
# 	cv2.imshow("cam", frame)
# 	key = cv2.waitKey(1) & 0xFF
        

# 	if key == ord("q"):
# 		break

# # do a bit of cleanup
# print("[INFO] cleaning up...")
# cv2.destroyAllWindows()
# webcam.stop()
