import cv2
import time

RTSP_URL = "rtsp://admin:@192.168.1.6:554/ch0_0.264"

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print("RTSP stream not opened")
    exit()

prev_time = time.time()

while True:
    start_time = time.time()

    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    if not ret:
        break

    # ------------------ BLACK & WHITE ------------------

    # ------------------ LATENCY CALC -------------------
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    latency_ms = (curr_time - start_time) * 1000

    # ------------------ DISPLAY INFO -------------------
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)

    cv2.putText(frame, f"Latency: {latency_ms:.1f} ms", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)

    cv2.imshow("RTSP BLACK & WHITE + LATENCY", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
