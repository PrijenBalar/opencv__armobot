import cv2
import numpy as np

vc = cv2.VideoCapture(0)

while cv2.waitKey(1) < 0:
    ret, frame = vc.read()
    blur = cv2.GaussianBlur(frame,(5,5),0)
    blur = cv2.flip(blur,1)
    _, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)
    cv2.imshow("blur",blur)
