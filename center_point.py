import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip camera (mirror)
    frame = cv2.flip(frame, 1)

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur to remove noise
    blur = cv2.GaussianBlur(gray, (7,7), 0)

    # Edge detection
    edges = cv2.Canny(blur, 50, 150)

    # Find contours (objects)
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for cnt in contours:
        area = cv2.contourArea(cnt)

        # Ignore small noise
        if area < 500 or area > 3000:
            continue

        # Bounding box
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

        #aspect ratio of object
        aspect_ratio = w / h



        # Centroid
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Draw centroid
            cv2.circle(frame, (cx, cy), 5, (0,0,255), -1)

            # Show coordinates
            cv2.putText(frame, f"Center: ({cx},{cy})",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0,255,0), 1)

    cv2.imshow("Object & Centroid Test", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
