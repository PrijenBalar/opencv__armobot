import cv2
import serial
import struct
import time

# ================= SETTINGS =================
RTSP_URL = 0              # 0 = webcam, or put RTSP URL
COM_PORT = "COM15"
BAUD = 460800

# ---- SAFE TELEMETRY SETTINGS ----
FRAME_WIDTH = 160
FRAME_HEIGHT = 120
JPEG_QUALITY = 8
FRAME_DELAY = 0.05        # ~4 FPS (safe)

print("Opening telemetry port...")

try:
    ser = serial.Serial(COM_PORT, BAUD, timeout=0)
    print("Telemetry connected on", COM_PORT)
except Exception as e:
    print("Failed to open telemetry:", e)
    exit()

print("Opening video source...")
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("Video stream not opened")
    exit()

print("Streaming started...")

frame_counter = 0
bytes_sent_total = 0
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # -------- Compression Pipeline --------
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # frame = cv2.GaussianBlur(frame, (7, 7), 0)

    _, encoded = cv2.imencode(
        '.jpg',
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
    )

    data = encoded.tobytes()

    # -------- Packet Structure --------
    # Header: 0xAA 0x55
    # Length: 2 bytes (big endian)
    # Payload: JPEG data
    packet = b'\xAA\x55' + struct.pack(">H", len(data)) + data

    try:
        ser.write(packet)
    except:
        print("Telemetry write failed")
        break

    frame_counter += 1
    bytes_sent_total += len(packet)

    # -------- Stats Every 1 Second --------
    if time.time() - start_time >= 1:
        elapsed = time.time() - start_time
        fps = frame_counter / elapsed
        kbps = (bytes_sent_total * 8) / 1000 / elapsed

        print("FPS:", round(fps, 2),
              "| Frame Size:", len(data), "bytes",
              "| Speed:", round(kbps, 1), "kbps")

        frame_counter = 0
        bytes_sent_total = 0
        start_time = time.time()

    time.sleep(FRAME_DELAY)

cap.release()
ser.close()
