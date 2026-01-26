import cv2
import cv2.aruco as aruco
import numpy as np
import time
from ArmControl import ArmControl

arm = ArmControl()

# ===================== TIMING =====================
POS_INTERVAL = 0.5
last_pos_time = 0

# ===================== STEPPER CALIBRATION =====================
stepper1 = 6   # mm / degree
stepper2 = 9
stepper3 = 6

# ===================== CONTROL TUNING =====================
DEAD_MM = 15
Y_DEAD_MM = 7
Z_DEAD_MM = 20

MIN_STEP = 2          # degrees
MAX_STEP = 6          # max degrees per update (GLOBAL speed)

# Camera → arm offsets (calibrated by you)
Y_OFFSET = 110
Z_OFFSET = 20

# ===================== MARKER IDS =====================
ARM_MARKER_ID = 23
TARGET_MARKER_ID = 19

# ===================== CAMERA CALIBRATION =====================
camera_matrix = np.load("cameraMatrix.npy")
dist_coeffs = np.load("distCoeffs.npy")

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
detector = aruco.ArucoDetector(aruco_dict, aruco.DetectorParameters())

cap = cv2.VideoCapture(0)

# ===================== MARKER GEOMETRY =====================
MARKER_SIZE_M = 0.053
obj_points = np.array([
    [-MARKER_SIZE_M/2,  MARKER_SIZE_M/2, 0],
    [ MARKER_SIZE_M/2,  MARKER_SIZE_M/2, 0],
    [ MARKER_SIZE_M/2, -MARKER_SIZE_M/2, 0],
    [-MARKER_SIZE_M/2, -MARKER_SIZE_M/2, 0]
], dtype=np.float32)

# ===================== MAIN LOOP =====================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()
    if now - last_pos_time > POS_INTERVAL:
        try:
            pos = arm.get_current_position()
        except:
            pos = None
        last_pos_time = now

        if pos:
            print(f"📍 J1:{pos['joint1']} J2:{pos['joint2']} J3:{pos['joint3']}")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)

    arm_pos = None
    target_pos = None

    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners, ids)

        for i, mid in enumerate(ids.flatten()):
            img_pts = corners[i][0].astype(np.float32)

            ok, _, tvec = cv2.solvePnP(
                obj_points, img_pts,
                camera_matrix, dist_coeffs,
                flags=cv2.SOLVEPNP_IPPE_SQUARE
            )
            if not ok:
                continue

            x = tvec[0][0] * 1000
            y = tvec[1][0] * 1000
            z = tvec[2][0] * 1000

            if mid == ARM_MARKER_ID:
                arm_pos = (x, y, z)
            elif mid == TARGET_MARKER_ID:
                target_pos = (x, y, z)

            cv2.putText(
                frame,
                f"ID:{mid} X:{int(x)} Y:{int(y)} Z:{int(z)}",
                (10, 30 + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 255, 0), 2
            )

    # ===================== CONTROL =====================
    if arm_pos and target_pos and pos:
        ax, ay, az = arm_pos
        tx, ty, tz = target_pos

        # ---- Camera error (mm) ----
        dx = (tx - 10) - ax
        dy = (ty - Y_OFFSET) - ay
        dz = (tz + Z_OFFSET) - az

        # ---- Global dead-zone ----
        if abs(dx) < DEAD_MM and abs(dy) < Y_DEAD_MM and abs(dz) < Z_DEAD_MM:
            d_j1 = d_j2 = d_j3 = 0
        else:
            # ---- Convert to joint space ----
            dj1_raw = -dx / stepper1
            dj2_raw =  dy / stepper2
            dj3_raw = -dz / stepper3

            # ---- Normalize vector (KEY LOGIC) ----
            max_mag = max(abs(dj1_raw), abs(dj2_raw), abs(dj3_raw), 1)

            d_j1 = int(dj1_raw / max_mag * MAX_STEP)
            d_j2 = int(dj2_raw / max_mag * MAX_STEP)
            d_j3 = int(dj3_raw / max_mag * MAX_STEP)

            # ---- Noise kill ----
            if abs(d_j1) < MIN_STEP: d_j1 = 0
            if abs(d_j2) < MIN_STEP: d_j2 = 0
            if abs(d_j3) < MIN_STEP: d_j3 = 0

        # ---- Send combined motion ----
        if pos:
            if d_j1 != 0:
                arm.move_joint(1, pos['joint1'] + d_j1)
            if d_j2 != 0:
                arm.move_joint(2, pos['joint2'] + d_j2)
            if d_j3 != 0:
                arm.move_joint(3, pos['joint3'] + d_j3)

        print(
            f"dx:{int(dx)} dy:{int(dy)} dz:{int(dz)} | "
            f"dJ1:{d_j1} dJ2:{d_j2} dJ3:{d_j3}"
        )

    cv2.imshow("Vector-Based ArUco Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
