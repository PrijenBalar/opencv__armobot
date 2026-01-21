import cv2
import numpy as np

vc = cv2.VideoCapture(0)

while cv2.waitKey(1) < 0:
    ret, frame = vc.read()
    frame = cv2.flip(frame,1)
    image = cv2.resize(frame,(500,500))
    cv2.circle(frame,(250,200),150,(0,0,255),10)
    cv2.imshow("video",frame)
