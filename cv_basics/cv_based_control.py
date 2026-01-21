import cv2
import mediapipe as mp
import time
import requests
import math

arm_connected = False

arm_angle = "0"
last_time_angle = time.time()

open_gripper_url = "http://192.168.4.1/gripper?action=open"
close_gripper_url = "http://192.168.4.1/gripper?action=close"

try:
    res = requests.get("http://192.168.4.1" , timeout=5)


    if res.status_code == 200:
        arm_connected = True
    else:
        arm_connected = False
except:
    arm_connected = False


handOpen = False

gripper_status = "open"
last_time = time.time()

# Webcam
cap = cv2.VideoCapture(1)

# MediaPipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

pTime = 0


def calculate_angle(a, b, c):
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])

    dot_product = ba[0]*bc[0] + ba[1]*bc[1]
    mag_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    mag_bc = math.sqrt(bc[0]**2 + bc[1]**2)

    angle = math.degrees(math.acos(dot_product / (mag_ba * mag_bc)))
    return angle

def pose_control():
    global arm_angle, open_gripper_url, close_gripper_url , arm_connected, gripper_status ,last_time_angle
    if pose_results.pose_landmarks:
        # mpDraw.draw_landmarks(
        #     frame,
        #     pose_results.pose_landmarks,
        #     mpPose.POSE_CONNECTIONS
        # )

        lm = pose_results.pose_landmarks.landmark

        # Left arm landmarks
        shoulder = lm[11]
        elbow = lm[13]
        wrist = lm[15]

        # Convert to pixel coordinates
        s = (int(shoulder.x * w), int(shoulder.y * h))
        e = (int(elbow.x * w), int(elbow.y * h))
        wri = (int(wrist.x * w), int(wrist.y * h))

        # Calculate angle
        angle = calculate_angle(s, e, wri)

        # Draw joints
        # cv2.circle(frame, s, 8, (255, 0, 0), cv2.FILLED)
        # cv2.circle(frame, e, 8, (0, 255, 0), cv2.FILLED)
        # cv2.circle(frame, wri, 8, (0, 0, 255), cv2.FILLED)

        # Show angle
        cv2.putText(frame, f"{int(angle)} deg",
                    (e[0] + 10, e[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


        dta = time.time() - last_time_angle
        print(f"Left Elbow Angle: {angle:.2f}" , dta)

        if arm_connected  and dta > 3:
            last_time_angle = time.time()
            if angle < 45  and arm_angle != "0":
                arm_angle = "0"
                res = requests.post("http://192.168.4.1/stepper?num=2&angle=0" , timeout=10)
                res = requests.post("http://192.168.4.1/stepper?num=3&angle=0", timeout=10)
                print("command send angle 0")

            elif angle > 45  and angle < 60 and arm_angle != "15" :
                print("command send angle 15")
                res = requests.post("http://192.168.4.1/stepper?num=2&angle=15" , timeout=10)
                res = requests.post("http://192.168.4.1/stepper?num=3&angle=15", timeout=10)
                arm_angle = "15"

            elif angle > 60  and angle < 90 and arm_angle != "30" :
                print("command send angle 30")
                res = requests.post("http://192.168.4.1/stepper?num=2&angle=30" , timeout=10)
                res = requests.post("http://192.168.4.1/stepper?num=3&angle=30", timeout=10)
                arm_angle = "30"

            elif angle > 90  and angle < 120 and arm_angle != "45" :
                print("command send angle 45")
                res = requests.post("http://192.168.4.1/stepper?num=2&angle=45" , timeout=10)
                res = requests.post("http://192.168.4.1/stepper?num=3&angle=45", timeout=10)
                arm_angle = "45"
            else:
                print("pass")



while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert to RGB
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    pose_results = pose.process(imgRGB)

    pose_control()


    lmList = []

    # Get landmarks
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

                # draw points
                if id in [4, 8, 12, 16, 20]:
                    cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

    # --------- Finger Status ---------
    fingers = []

    if len(lmList) != 0:
        # Thumb

        if lmList[4][1] > lmList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other fingers
        tips = [8, 12, 16, 20]
        for tip in tips:
            if lmList[tip][2] < lmList[tip - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        totalFingers = fingers.count(1)

        # --------- Boolean State ---------

        if totalFingers >= 3:
            handOpen = True
        elif totalFingers <= 2:
            handOpen = False


        dt = (time.time() - last_time)
        try:
            if handOpen and arm_connected:

                if dt > 1 and gripper_status != "open":
                    last_time = time.time()
                    res = requests.get(open_gripper_url, timeout=10)
                    if res.status_code == 200:
                        gripper_status = "open"


                    time.sleep(0.1)

            if handOpen == False and arm_connected :

                if dt > 1 and gripper_status != "close":
                    gripper_status = "close"
                    last_time = time.time()
                    res = requests.get(close_gripper_url , timeout=10)
                    if res.status_code == 200:
                        gripper_status = "close"

                    time.sleep(0.1)
        except:
            pass

        # Display
        print("totalFingers" , totalFingers , dt , gripper_status)

        cv2.putText(frame, f"Fingers: {totalFingers}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

        cv2.putText(frame, f"Hand Open: {handOpen}", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    # FPS
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(frame, f"FPS: {int(fps)}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

    cv2.imshow("Hand Open Detection", frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()