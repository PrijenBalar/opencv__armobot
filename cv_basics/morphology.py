import cv2
import numpy as np

vc = cv2.VideoCapture(0)

while cv2.waitKey(1) < 0:
    ret, frame = vc.read()
    frame = cv2.flip(frame, 1)

    # 1) Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2) Blur to remove noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3) Threshold
    _, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)

    # 4) Morphological opening (remove small dots)
    #kernel = np.ones((3, 3), np.uint8)
    #opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # 5) Closing
    kernel = np.ones((5, 5), np.uint8)
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # 5) Show results
    cv2.imshow("Threshold", thresh)
    #cv2.imshow("After Opening", opening)
    cv2.imshow("closing", closing)