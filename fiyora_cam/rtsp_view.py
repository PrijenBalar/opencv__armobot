import cv2
import numpy as np
import time

cam1 = "rtsp://admin:123456@192.168.1.100:554/ch01.264"
cam2 = "rtsp://admin:123456@192.168.1.101:554/ch01.264"


def connect_camera(url):
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera: {url}")
        return None

    print(f"[INFO] Connected to {url}")
    return cap


cap1 = connect_camera(cam1)
cap2 = connect_camera(cam2)

while True:

    try:

        if cap1 is None or cap2 is None:
            print("[INFO] Reconnecting cameras...")
            cap1 = connect_camera(cam1)
            cap2 = connect_camera(cam2)
            time.sleep(2)
            continue

        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or frame1 is None:
            print("[WARNING] Camera 1 frame lost")
            cap1.release()
            cap1 = connect_camera(cam1)
            continue

        if not ret2 or frame2 is None:
            print("[WARNING] Camera 2 frame lost")
            cap2.release()
            cap2 = connect_camera(cam2)
            continue

        # resize frames
        frame1 = cv2.resize(frame1, (320, 320))
        frame2 = cv2.resize(frame2, (320, 320))

        # combine frames
        combined = np.hstack((frame1, frame2))

        cv2.imshow("Two Camera View", combined)

        key = cv2.waitKey(1)
        if key == 27:  # ESC key
            print("[INFO] Exit requested")
            break

    except Exception as e:
        print("[ERROR]", e)
        time.sleep(1)

if cap1:
    cap1.release()

if cap2:
    cap2.release()

cv2.destroyAllWindows()