import cv2
import numpy as np

def nothing(x):
    pass

cap = cv2.VideoCapture(0)

cv2.namedWindow("Parameters")
cv2.createTrackbar("Threshold1", "Parameters", 150, 255, nothing)
cv2.createTrackbar("Threshold2", "Parameters", 255, 255, nothing)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)

    t1 = cv2.getTrackbarPos("Threshold1", "Parameters")
    t2 = cv2.getTrackbarPos("Threshold2", "Parameters")

    edges = cv2.Canny(blur, t1, t2)

    cv2.imshow("Result", edges)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
