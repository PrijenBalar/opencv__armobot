import cv2
import numpy as np
import time
#import serial
import requests

PICO_IP = "192.168.0.205"


# 🔌 Arduino COM port
#ser = serial.Serial("COM6", 9600)  # change COM if needed

RTSP_URL = "rtsp://admin:123456@192.168.0.100:554/ch01.264"

cap = cv2.VideoCapture(RTSP_URL)

triggered = False
last_seen = 0
trigger_time = 0
buzzer_on = False

STOP_DELAY = 5.0
BUZZER_DELAY = 5.0

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
    if not ret:
        print("Stream failed")
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_green = np.array([40, 80, 80])
    upper_green = np.array([80, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    edges = cv2.Canny(mask, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = False

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < 1000:
            continue

        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(cnt)

            aspect_ratio = w / float(h)

            if 0.5 < aspect_ratio < 2.0:
                detected = True
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

    current_time = time.time()

    # ---------------- TRIGGER ----------------
    if detected:
        last_seen = current_time

        if not triggered:
            print("TRIGGER")
            triggered = True
            trigger_time = current_time

        if not buzzer_on:
            try:
                requests.get(f"http://{PICO_IP}/on", timeout=0.2)
                buzzer_on = True
            except:
                print("Pico not reachable")

    # ---------------- STOP ----------------
    else:
        if triggered and (current_time - last_seen > STOP_DELAY):
            print("STOP")
            triggered = False

            if buzzer_on:
                try:
                    requests.get(f"http://{PICO_IP}/off", timeout=5)
                    buzzer_on = False
                except:
                    print("Pico not reachable")

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
#ser.close()
cv2.destroyAllWindows()