import cv2
import cv2.aruco as aruco
import numpy as np
import time

# ===================== CALIBRATION =====================
stepper1 = 6
stepper2 = 9
stepper3 = 6

DEAD_MM = 15
Y_DEAD_MM = 7
Z_DEAD_MM = 20

MIN_STEP = 2
MAX_STEP_SMALL = 4
MAX_STEP_MED = 10
MAX_STEP_LARGE = 18

ARM_MARKER_ID = 23
TARGET_MARKER_ID = 19

camera_matrix = np.load("cameraMatrix.npy")
dist_coeffs = np.load("distCoeffs.npy")

MARKER_SIZE_M = 0.053
obj_points = np.array([
    [-MARKER_SIZE_M/2,  MARKER_SIZE_M/2, 0],
    [ MARKER_SIZE_M/2,  MARKER_SIZE_M/2, 0],
    [ MARKER_SIZE_M/2, -MARKER_SIZE_M/2, 0],
    [-MARKER_SIZE_M/2, -MARKER_SIZE_M/2, 0]
], dtype=np.float32)

def adaptive_limit(d):
    d = abs(d)
    if d > 80:
        return MAX_STEP_LARGE
    if d > 40:
        return MAX_STEP_MED
    return MAX_STEP_SMALL

# ===================== VISION THREAD =====================
def vision_loop(command_queue):
    print("👁️ Vision thread started")

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Camera not opened")
        return

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
    detector = aruco.ArucoDetector(aruco_dict, aruco.DetectorParameters())

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)

        arm_pos = None
        target_pos = None

        if ids is not None:
            aruco.drawDetectedMarkers(frame, corners, ids)

            for i, mid in enumerate(ids.flatten()):
                ok, _, tvec = cv2.solvePnP(
                    obj_points,
                    corners[i][0],
                    camera_matrix,
                    dist_coeffs,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE
                )
                if not ok:
                    continue

                x, y, z = (tvec * 1000).flatten()

                if mid == ARM_MARKER_ID:
                    arm_pos = (x, y, z)
                elif mid == TARGET_MARKER_ID:
                    target_pos = (x, y, z)

                # ✅ SHOW XYZ ON CAMERA
                cv2.putText(
                    frame,
                    f"ID:{mid} X:{int(x)} Y:{int(y)} Z:{int(z)}",
                    (10, 30 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        if arm_pos and target_pos:
            ax, ay, az = arm_pos
            tx, ty, tz = target_pos

            dx = (tx - 10) - ax
            dy = (ty - 110) - ay
            dz = (tz + 20) - az

            d_j1 = d_j2 = d_j3 = 0

            if abs(dx) > DEAD_MM:
                d_j1 = max(-adaptive_limit(dx), min(adaptive_limit(dx), int(-dx / stepper1)))
            if abs(dy) > Y_DEAD_MM:
                d_j2 = max(-adaptive_limit(dy), min(adaptive_limit(dy), int(dy / stepper2)))
            if abs(dz) > Z_DEAD_MM:
                d_j3 = max(-adaptive_limit(dz), min(adaptive_limit(dz), int(-dz / stepper3)))

            if abs(d_j1) < MIN_STEP: d_j1 = 0
            if abs(d_j2) < MIN_STEP: d_j2 = 0
            if abs(d_j3) < MIN_STEP: d_j3 = 0

            cmd = (d_j1, d_j2, d_j3)

            if not command_queue.full():
                command_queue.put(cmd)

            print("VISION →", cmd)

        cv2.imshow("Vision", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
