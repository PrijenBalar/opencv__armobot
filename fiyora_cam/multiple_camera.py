import cv2
import numpy as np
import threading
import time
import math
import requests

RTSP_URLS = [
    "rtsp://admin:123456@192.168.0.100:554/ch01.264",
    "rtsp://admin:123456@192.168.0.101:554/ch01.264",
    "rtsp://admin:123456@192.168.0.102:554/ch01.264",
    "rtsp://admin:123456@192.168.0.103:554/ch01.264",
]
PICO_IP = "192.168.0.205"


triggered = False
last_seen = 0
trigger_time = 0
buzzer_on = False

STOP_DELAY = 5.0
BUZZER_DELAY = 5.0


# Shared frames
frames = [np.zeros((270, 480, 3), dtype=np.uint8) for _ in RTSP_URLS]

def human_detection(frame):
    global last_seen , buzzer_on , trigger_time , triggered
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
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

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


class CameraThread:
    def __init__(self, url, index):
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.index = index
        self.running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        global frames
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frames[self.index] = cv2.resize(frame, (480, 270))
            else:
                frames[self.index] = np.zeros((270, 480, 3), dtype=np.uint8)

    def stop(self):
        self.running = False
        self.cap.release()

# Start all camera threads
cams = [CameraThread(url, i) for i, url in enumerate(RTSP_URLS)]

while True:
    # start_time = time.time()

    current_frames = frames.copy()
    n = len(current_frames)

    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    # Fill empty
    while len(current_frames) < rows * cols:
        current_frames.append(np.zeros((540, 720, 3), dtype=np.uint8))

    # Build grid
    grid_rows = []
    for i in range(rows):
        row = np.hstack(current_frames[i*cols:(i+1)*cols])
        grid_rows.append(row)

    grid = np.vstack(grid_rows)

    # Optional: force 1920x1080
    grid = cv2.resize(grid, (1200, 700))

    # print("Loop time:", time.time() - start_time)
    human_detection(grid)

    cv2.imshow("Multi-thread Grid", grid)

    if cv2.waitKey(1) == 27:
        break

# Stop threads
for cam in cams:
    cam.stop()

cv2.destroyAllWindows()