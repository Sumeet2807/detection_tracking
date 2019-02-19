# USAGE
# python motion_detector.py
# python motion_detector.py --video videos/example_01.mp4

# import the necessary packages
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import numpy as np
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=250, help="minimum area size")
args = vars(ap.parse_args())


vs = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None
frame_count = 0
frame_centroids = []

# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	

	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if frame is None:
		break

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	(H, W) = frame.shape[:2]
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
	frame_count += 1

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

file_name = args["video"] + ".pyd"
with open(file_name, "wb") as f:
	pickle.dump(frame_centroids,f)
	

# cleanup the camera and close any open windows

# x_plt = []
# y_plt = []
# z_plt = []
# for cntrs in frame_centroids:
# 	for val in cntrs[1]:
# 		x_plt.append(val[0])
# 		y_plt.append(val[1])
# 		z_plt.append(cntrs[0])

# fig = plt.figure()
# ax = fig.add_subplot(111, projection = "3d") 	
# ax.scatter(x_plt, z_plt, y_plt,)
# #ax.axis([0,W,0,600,H,0])
# # plt.scatter(x_plt, y_plt, s=1)
# # plt.axis([0,W,H,0])
# plt.show()


vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()