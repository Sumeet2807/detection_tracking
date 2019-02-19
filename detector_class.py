import cv2
import imutils
import numpy as np
from imutils.object_detection import non_max_suppression



class detector_mul:

	first_frame_set = None

	def __init__(self, type):		

		self.type = type

		if self.type == "hog":
			self.hog = cv2.HOGDescriptor()
			self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
			

	def detect(self, frame):

		boxes = []

		if self.type == "motion":


			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			gray = cv2.GaussianBlur(gray, (21, 21), 0)
			if self.first_frame_set is None:
				self.firstFrame = gray
				self.first_frame_set = 1
				return boxes

			frameDelta = cv2.absdiff(self.firstFrame, gray)
			thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]	
			thresh = cv2.dilate(thresh, None, iterations=2)
			cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE)
			cnts = imutils.grab_contours(cnts)
			for c in cnts:

				(x, y, w, h) = cv2.boundingRect(c)
				boxes.append((x, y, w, h))
				

		elif self.type == "hog":

			(rects, weights) = self.hog.detectMultiScale(frame, winStride=(4, 4),padding=(8, 8), scale=1.05)
			rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
			pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
			for (xa, ya, xb, yb) in pick:
				boxes.append((xa, ya, xb-xa, yb-ya))

		return boxes

