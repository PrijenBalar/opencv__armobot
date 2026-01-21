import cv2
import numpy as np


vc=cv2.VideoCapture(0)

while cv2.waitKey(1) <0:
    hasFrame, frame = vc.read()
    frame = frame[0:500,0:500]

    height,width,depth = frame.shape
    print(frame.shape)

    frame[0:50,:,1]=255
    frame[-50:height,:,2]=0


    cv2.imshow("WEB CAM",frame)
