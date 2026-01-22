import cv2
import cv2.aruco as aruco
import numpy as np
import time
from ArmControl import ArmControl
arm=ArmControl()

last_pos_time = 0
POS_INTERVAL = 1   # seconds

stepper1 = 6   # mm / degree
stepper2 = 9
stepper3 = 6



# ===================== LOAD CAMERA CALIBRATION =====================
camera_matrix = np.load("cameraMatrix.npy")
dist_coeffs = np.load("distCoeffs.npy")

# ===================== ARUCO SETUP =====================
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# ===================== CAMERA =====================
cap = cv2.VideoCapture(0)

# ===================== MARKER INFO =====================
MARKER_SIZE_M = 0.053 # marker size in METERS (5 cm)

# 3D object points of marker corners (meters)
obj_points = np.array([
    [-MARKER_SIZE_M/2,  MARKER_SIZE_M/2, 0],
    [ MARKER_SIZE_M/2,  MARKER_SIZE_M/2, 0],
    [ MARKER_SIZE_M/2, -MARKER_SIZE_M/2, 0],
    [-MARKER_SIZE_M/2, -MARKER_SIZE_M/2, 0]
], dtype=np.float32)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()

    if now - last_pos_time >= POS_INTERVAL:
        pos = arm.get_current_position()
        last_pos_time = now

        if pos:
            print(
                f"📍 J1:{pos['joint1']}  "
                f"J2:{pos['joint2']}  "
                f"J3:{pos['joint3']}"
            )

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, _ = detector.detectMarkers(gray)

    arm_pos = None
    target_pos = None

    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners, ids)

        for i, marker_id in enumerate(ids.flatten()):
            img_points = corners[i][0].astype(np.float32)

            success, rvec, tvec = cv2.solvePnP(
                obj_points,
                img_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_IPPE_SQUARE
            )
            if not success:
                continue

            x_mm = int(tvec[0][0] * 1000)
            y_mm = int(tvec[1][0] * 1000)
            z_mm = int(tvec[2][0] * 1000)

            # ARM MARKER
            if marker_id == 23:
                arm_pos = (x_mm, y_mm, z_mm)

            # DESTINATION MARKER
            elif marker_id == 19:
                target_pos = (x_mm, y_mm, z_mm)

            cv2.putText(
                frame,
                f"ID:{marker_id} X:{x_mm} Y:{y_mm} Z:{z_mm}",
                (10, 30 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
            if arm_pos and target_pos:
                ax, ay, az = arm_pos
                tx, ty, tz = target_pos

                dx = tx - ax  # IMPORTANT: target - arm

                DEAD_MM = 10
                STEP_LIMIT = 4  # smooth but fast

                if abs(dx) < DEAD_MM:
                    d_j1 = 0
                else:
                    d_j1 = int(-dx / stepper1)
                    d_j1 = max(-STEP_LIMIT, min(STEP_LIMIT, d_j1))

                if d_j1 != 0:
                    j1_cur = int(pos['joint1'])
                    j1_new = j1_cur + d_j1
                    j1_new = max(-175, min(175, j1_new))
                    arm.move_joint(1, j1_new)

                print(
                    f"ARM X:{ax} → TARGET X:{tx} | dx:{dx} | dJ1:{d_j1}"
                )

            # ===================== PRINT (FOR ROBOT USE) =====================
                # print(
                #     f"Marker {ids[i][0]} -> "
                #     f"X:{x_mm:.2f} mm, "
                #     f"Y:{y_mm:.2f} mm, "
                #     f"Z:{z_mm:.2f} mm"
                # )

    cv2.imshow("ArUco solvePnP (mm)", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
