import cv2
import numpy as np

cam1 = "rtsp://admin:123456@192.168.1.100:554/ch01.264"
cam2 = "rtsp://admin:123456@192.168.1.101:554/ch01.264"

cap1 = cv2.VideoCapture(cam1, cv2.CAP_FFMPEG)
cap2 = cv2.VideoCapture(cam2, cv2.CAP_FFMPEG)

cap1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap2.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while True:

    cap1.grab()
    cap2.grab()

    ret1, frame1 = cap1.retrieve()
    ret2, frame2 = cap2.retrieve()

    if not ret1 or not ret2:
        print("Stream error")
        break

    # Main camera
    frame1 = cv2.resize(frame1, (640, 480))

    # Sub-screen camera
    sub = cv2.resize(frame2, (200, 150))

    # position of subscreen (top-right corner)
    x_offset = 640 - 210
    y_offset = 10

    frame1[y_offset:y_offset+150, x_offset:x_offset+200] = sub

    cv2.imshow("Camera View", frame1)

    if cv2.waitKey(1) == 27:
        break

cap1.release()
cap2.release()
cv2.destroyAllWindows()