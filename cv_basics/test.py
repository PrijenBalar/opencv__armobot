import cv2
import mediapipe as mp

# ---------- MEDIAPIPE SETUP ----------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ---------- CAMERA ----------
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Convert BGR → RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame
    result = hands.process(rgb)

    # ---------- IF HAND DETECTED ----------
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            # Draw hand landmarks + connections
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Example: get INDEX finger tip (id = 8)
            h, w, _ = frame.shape
            lm = hand_landmarks.landmark[8]
            cx, cy = int(lm.x * w), int(lm.y * h)

            cv2.circle(frame, (cx, cy), 10, (0, 0, 255), -1)
            cv2.putText(frame, "Index Tip",
                        (cx + 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 0, 255), 2)

    # ---------- DISPLAY ----------
    cv2.imshow("MediaPipe Hands - Test", frame)

    if cv2.waitKey(1) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
