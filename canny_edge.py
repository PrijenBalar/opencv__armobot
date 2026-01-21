import cv2
import numpy as np

vc = cv2.VideoCapture(0)

while cv2.waitKey(1) < 0:
    ret, frame = vc.read()
    blur = cv2.GaussianBlur(frame,(1,1),0)
    blur = cv2.flip(blur,1)
    edges = cv2.Canny(blur, 50, 150)
    cv2.imshow("Edges", edges)