import cv2
import mediapipe as mp
import numpy as np

# ================== CAMERA ==================
cap = cv2.VideoCapture(0)
FRAME_W = 640
FRAME_H = 480
cap.set(3, FRAME_W)
cap.set(4, FRAME_H)

CENTER_X = FRAME_W // 2
CENTER_Y = FRAME_H // 2

# ================== MEDIAPIPE HAND ==================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ================== MAIN LOOP ==================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # Draw camera center
    cv2.circle(frame, (CENTER_X, CENTER_Y), 5, (255, 0, 0), -1)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:

            # ===== HAND BOUNDING BOX =====
            xs = [lm.x for lm in hand.landmark]
            ys = [lm.y for lm in hand.landmark]

            x1 = int(min(xs) * FRAME_W)
            y1 = int(min(ys) * FRAME_H)
            x2 = int(max(xs) * FRAME_W)
            y2 = int(max(ys) * FRAME_H)

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(FRAME_W, x2), min(FRAME_H, y2)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            hand_roi = frame[y1:y2, x1:x2]
            if hand_roi.size == 0:
                continue

            # ===== REMOVE SKIN COLOR =====
            hsv = cv2.cvtColor(hand_roi, cv2.COLOR_BGR2HSV)

            # Tuned for real skin tones
            lower_skin = np.array([0, 20, 70])
            upper_skin = np.array([20, 255, 255])

            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)

            # Invert → keep object
            object_mask = cv2.bitwise_not(skin_mask)

            kernel = np.ones((5, 5), np.uint8)
            object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_OPEN, kernel)
            object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_CLOSE, kernel)

            # ===== FIND OBJECT =====
            contours, _ = cv2.findContours(
                object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            roi_area = hand_roi.shape[0] * hand_roi.shape[1]
            valid = []

            for c in contours:
                area = cv2.contourArea(c)
                if 500 < area < roi_area * 0.6:
                    valid.append(c)

            if not valid:
                continue

            c = max(valid, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)

            # ===== OBJECT DATA =====
            obj_cx = x1 + x + w // 2
            obj_cy = y1 + y + h // 2
            diameter = int((w + h) / 2)

            # Draw object
            cv2.rectangle(frame,
                          (x1 + x, y1 + y),
                          (x1 + x + w, y1 + y + h),
                          (0, 0, 255), 2)

            cv2.circle(frame, (obj_cx, obj_cy), 5, (0, 0, 255), -1)

            # ===== GIMBAL ERROR =====
            error_x = obj_cx - CENTER_X
            error_y = obj_cy - CENTER_Y

            # ===== DISPLAY =====
            cv2.putText(frame, f"Err X: {error_x}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Err Y: {error_y}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Diameter: {diameter}px", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # ===== DEBUG WINDOWS (OPTIONAL) =====
            cv2.imshow("Skin Mask", skin_mask)
            cv2.imshow("Object Mask", object_mask)

    cv2.imshow("Hand Object Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
