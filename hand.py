import cv2
import mediapipe as mp
import time

import requests

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

pTime = 0

last_time = time.time()

open_gripper = "http://192.168.4.1/gripper?action=open"

close_gripper = "http://192.168.4.1/gripper?action=close"



while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    lmList = []

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

                # Draw finger tips
                if id in [4, 8, 12, 16, 20]:
                    cv2.circle(img, (cx, cy), 12, (255, 0, 255), cv2.FILLED)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # --------- Finger Counting ---------
    fingers = []

    if len(lmList) != 0:
        # Thumb
        if lmList[4][1] > lmList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 fingers
        tips = [8, 12, 16, 20]
        for tip in tips:
            if lmList[tip][2] < lmList[tip - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        totalFingers = fingers.count(1)

        # --------- Boolean State ---------
        handOpen = False
        if totalFingers >= 4:
            handOpen = True
            if time.time() - last_time > 2:
                res = requests.get(open_gripper)
                last_time = time.time()

        elif totalFingers <= 1:
            handOpen = False
            if time.time() - last_time > 2:
                res = requests.get(close_gripper)
                last_time = time.time()


        # Display
        cv2.putText(img, f"Fingers: {totalFingers}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.putText(img, f"Hand Open: {handOpen}", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # --------- FPS ---------
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f"FPS: {int(fps)}", (10, 40),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

    cv2.imshow("Hand Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
