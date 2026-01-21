import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Convert to gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 1️⃣ Simple Binary Threshold (LOW)
    _, thresh_low = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

    # 2️⃣ Simple Binary Threshold (HIGH)
    _, thresh_high = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    # 3️⃣ Inverse Binary Threshold
    _, thresh_inv = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)

    # 4️⃣ Adaptive Threshold (auto lighting)
    thresh_adapt = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    # Show all frames
    cv2.imshow("Original", frame)
    cv2.imshow("Gray", gray)
    cv2.imshow("Binary TH=100", thresh_low)
    cv2.imshow("Binary TH=160", thresh_high)
    cv2.imshow("Binary INV (160)", thresh_inv)
    cv2.imshow("Adaptive Threshold", thresh_adapt)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
