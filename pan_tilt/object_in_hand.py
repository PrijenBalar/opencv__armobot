import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import serial
import time

# ---------------- SERIAL ----------------
ser = serial.Serial('COM6', 9600, timeout=1)
time.sleep(2)
print("Connected to Arduino")

pan = 90
tilt = 90
last_pan = pan
last_tilt = tilt

dx = dy = 0
obj_cx = obj_cy = -1
ser.write(f"{pan},{tilt}\n".encode())


# ================== CONFIG & SMOOTHING ==================
FRAME_W, FRAME_H = 640, 480
CENTER_X, CENTER_Y = FRAME_W // 2, FRAME_H // 2
deg_per_pixel_x, deg_per_pixel_y = 60.0 / FRAME_W, 45.0 / FRAME_H

buffer_size = 3  # Reduced buffer for faster response on small items
x_buffer, y_buffer = deque(maxlen=buffer_size), deque(maxlen=buffer_size)

# ================== CAMERA & MEDIAPIPE ==================
cap = cv2.VideoCapture(0)
cap.set(3, FRAME_W)
cap.set(4, FRAME_H)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)



while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    object_mask = np.zeros((FRAME_H, FRAME_W), dtype=np.uint8)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    cv2.line(frame, (CENTER_X - 15, CENTER_Y), (CENTER_X + 15, CENTER_Y), (255, 0, 0), 2)
    cv2.line(frame, (CENTER_X, CENTER_Y - 15), (CENTER_X, CENTER_Y + 15), (255, 0, 0), 2)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            h_pts = np.array([[int(lm.x * FRAME_W), int(lm.y * FRAME_H)] for lm in hand_landmarks.landmark])
            hx, hy, hw, hh = cv2.boundingRect(h_pts)
            cv2.rectangle(frame, (hx - 15, hy - 15), (hx + hw + 15, hy + hh + 15), (0, 255, 0), 2)

            # 1. SILHOUETTE MASK
            hand_hull = cv2.convexHull(h_pts)
            hand_mask = np.zeros((FRAME_H, FRAME_W), dtype=np.uint8)
            cv2.fillConvexPoly(hand_mask, hand_hull, 255)

            # 2. SKIN DETECTION
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 30, 40])  # Slightly lowered saturation floor
            upper_skin = np.array([25, 255, 255])
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            skin_in_hand = cv2.bitwise_and(skin_mask, skin_mask, mask=hand_mask)

            # 3. OBJECT DETECTION
            object_mask = cv2.bitwise_xor(hand_mask, skin_in_hand)

            # Use smaller 3x3 or 5x5 kernel so small objects don't disappear
            kernel_small = np.ones((3, 3), np.uint8)
            object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_OPEN, kernel_small)
            object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_CLOSE, kernel_small)

            # 4. FIND CONTOURS
            contours, _ = cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid_objects = []

            for c in contours:
                area = cv2.contourArea(c)
                # CHANGE: Lowered from 1000 to 250 to catch small objects
                if 250 < area < 15000:
                    hull = cv2.convexHull(c)
                    solidity = float(area) / cv2.contourArea(hull) if cv2.contourArea(hull) > 0 else 0

                    # Solidity check for small items
                    if solidity > 0.6:
                        valid_objects.append(c)

            if valid_objects:
                best_c = max(valid_objects, key=cv2.contourArea)
                ox, oy, ow, oh = cv2.boundingRect(best_c)

                # ---------------- OBJECT POSITION ----------------
                obj_raw_x = ox + ow // 2
                obj_raw_y = oy + oh // 2

                x_buffer.append(obj_raw_x)
                y_buffer.append(obj_raw_y)

                obj_cx = int(sum(x_buffer) / len(x_buffer))
                obj_cy = int(sum(y_buffer) / len(y_buffer))

                cv2.rectangle(frame, (ox, oy), (ox + ow, oy + oh), (0, 0, 255), 2)
                cv2.circle(frame, (obj_cx, obj_cy), 5, (0, 0, 255), -1)

                # ---------------- ERROR ----------------
                dx = obj_cx - CENTER_X
                dy = obj_cy - CENTER_Y

                DEAD_ZONE = 12
                if abs(dx) < DEAD_ZONE:
                    dx = 0
                if abs(dy) < DEAD_ZONE:
                    dy = 0

                # ---------------- SERVO CONTROL ----------------
                GAIN = 0.15
                MAX_STEP = 2

                pan_before = pan
                tilt_before = tilt

                pan += dx * deg_per_pixel_x * GAIN
                tilt -= dy * deg_per_pixel_y * GAIN

                pan = max(last_pan - MAX_STEP, min(last_pan + MAX_STEP, pan))
                tilt = max(last_tilt - MAX_STEP, min(last_tilt + MAX_STEP, tilt))

                pan = int(max(0, min(180, pan)))
                tilt = int(max(0, min(180, tilt)))

                # ---------------- SEND ----------------
                if pan != last_pan or tilt != last_tilt:
                    cmd = f"{pan},{tilt}"
                    ser.write((cmd + "\n").encode())
                    last_pan, last_tilt = pan, tilt

                    print(
                        f"OBJ=({obj_cx},{obj_cy}) | "
                        f"ERR=({dx},{dy}) | "
                        f"PAN:{pan_before}->{pan} | "
                        f"TILT:{tilt_before}->{tilt}"
                    )
                # ----------- HUD (ALWAYS DRAW) -----------
                y0 = 20
                step = 22

                cv2.putText(frame, f"Object: ({obj_cx},{obj_cy})", (10, y0),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                cv2.putText(frame, f"Center: ({CENTER_X},{CENTER_Y})", (10, y0 + step),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                cv2.putText(frame, f"Error dx:{dx} dy:{dy}", (10, y0 + 2 * step),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                cv2.putText(frame, f"Pan:{pan}  Tilt:{tilt}", (10, y0 + 3 * step),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                cv2.putText(frame, f"Servo Sent:{last_pan},{last_tilt}", (10, y0 + 4 * step),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)



            else:
                x_buffer.clear()
                y_buffer.clear()
                obj_cx = obj_cy = -1
                dx = dy = 0

    cv2.imshow("Hand & Object Tracker", frame)
    cv2.imshow("Debug: Object Detection", object_mask)

    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()