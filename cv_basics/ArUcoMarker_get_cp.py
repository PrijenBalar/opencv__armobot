import cv2
import cv2.aruco as aruco
import numpy as np
import time
from ArmControl import ArmControl

arm = ArmControl()

# ====== TIMING / CONTROL ======
last_pos_time = 0
POS_INTERVAL = 0.5  # seconds

# ====== MACHINE / CALIBRATION ======
stepper1 = 6   # mm per degree (base)
stepper2 = 9
stepper3 = 6

# ====== CONTROL TUNING ======
DEAD_MM = 15          # deadband for x/z (mm)
Y_DEAD_MM = 15        # small deadband -> consider "arrived"
Y_RESTART_MM = 25     # must exceed this to *start* moving again
MIN_STEP = 2          # minimum step (degrees) to overcome rounding/noise
MAX_STEP_SMALL = 4
MAX_STEP_MED = 10
MAX_STEP_LARGE = 18

# ====== IDs ======
ARM_MARKER_ID = 23
TARGET_MARKER_ID = 19

# ====== persistence to avoid sending same command again ======
last_j1_cmd = None
last_j2_cmd = None
last_j3_cmd = None

# ====== Y state (hysteresis) ======
y_active = False      # If True, we are currently actively moving stepper-2

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
MARKER_SIZE_M = 0.053  # marker size in METERS (5.3 cm)

# 3D object points of marker corners (meters)
obj_points = np.array([
    [-MARKER_SIZE_M/2,  MARKER_SIZE_M/2, 0],
    [ MARKER_SIZE_M/2,  MARKER_SIZE_M/2, 0],
    [ MARKER_SIZE_M/2, -MARKER_SIZE_M/2, 0],
    [-MARKER_SIZE_M/2, -MARKER_SIZE_M/2, 0]
], dtype=np.float32)


def adaptive_limit(distance_mm):
    """Return an integer step limit (degrees) based on distance (mm)."""
    ad = abs(distance_mm)
    if ad > 80:
        return MAX_STEP_LARGE
    if ad > 40:
        return MAX_STEP_MED
    return MAX_STEP_SMALL


while True:
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()
    if now - last_pos_time >= POS_INTERVAL:
        pos = None
        try:
            pos = arm.get_current_position()
        except Exception:
            pos = None
        last_pos_time = now

        if pos:
            print(f"📍 J1:{pos['joint1']}  J2:{pos['joint2']}  J3:{pos['joint3']}")

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

            x_mm = float(tvec[0][0]) * 1000.0
            y_mm = float(tvec[1][0]) * 1000.0
            z_mm = float(tvec[2][0]) * 1000.0

            if marker_id == ARM_MARKER_ID:
                arm_pos = (x_mm, y_mm, z_mm)
            elif marker_id == TARGET_MARKER_ID:
                target_pos = (x_mm, y_mm, z_mm)

            cv2.putText(
                frame,
                f"ID:{int(marker_id)} X:{int(x_mm)} Y:{int(y_mm)} Z:{int(z_mm)}",
                (10, 30 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        if arm_pos and target_pos and pos:
            ax, ay, az = arm_pos
            tx, ty, tz = target_pos

            # ---------- X axis (unchanged logic) ----------
            dx = (tx - 10.0) - ax
            if abs(dx) < DEAD_MM:
                d_j1 = 0
            else:
                d_j1 = int(-dx / stepper1)
                limit = adaptive_limit(dx)
                if abs(d_j1) < MIN_STEP:
                    d_j1 = 0
                d_j1 = max(-limit, min(limit, d_j1))

            if d_j1 == 0:
                last_j1_cmd = None

            if d_j1 != 0 and pos:
                j1_cur = int(pos['joint1'])
                j1_new = j1_cur + d_j1
                # j1_new = max(-175, min(175, j1_new))
                if last_j1_cmd is None or j1_new != last_j1_cmd:
                    arm.move_joint(1, j1_new)
                    last_j1_cmd = j1_new

            # ---------- Y axis (stepper-2) with hysteresis ----------
            dy = ty - ay   # positive -> target higher than arm
            abs_dy = abs(dy)

            d_j2 = 0
            # If currently inactive, require larger movement to start (avoid small restarts)
            if not y_active:
                if abs_dy > Y_RESTART_MM:
                    # start active control
                    y_active = True
                else:
                    d_j2 = 0

            # If active, stop only when within the smaller deadband
            if y_active:
                if abs_dy < Y_DEAD_MM:
                    d_j2 = 0
                    y_active = False   # go to inactive; next start needs Y_RESTART_MM
                else:
                    # compute continuous step, then enforce minimum step and limits
                    raw = dy / stepper2
                    # ensure a minimum step to overcome rounding/noise
                    if abs(raw) < MIN_STEP:
                        raw = MIN_STEP if raw > 0 else -MIN_STEP
                    limit_y = adaptive_limit(dy)
                    d_j2 = int(max(-limit_y, min(limit_y, raw)))

            # unlock when stopped to allow direction reversal on new movement
            if d_j2 == 0:
                last_j2_cmd = None

            if d_j2 != 0 and pos:
                j2_cur = int(pos['joint2'])
                j2_new = j2_cur + d_j2
                j2_new = max(-20, min(47, j2_new))
                if last_j2_cmd is None or j2_new != last_j2_cmd:
                    arm.move_joint(2, j2_new)
                    last_j2_cmd = j2_new

            # ---------- Z axis (same idea as before) ----------
            dz = tz - az
            if abs(dz) < DEAD_MM:
                d_j3 = 0
            else:
                d_j3 = -int(dz / stepper3)
                limit_z = adaptive_limit(dz)
                if abs(d_j3) < MIN_STEP:
                    d_j3 = 0
                d_j3 = max(-limit_z, min(limit_z, d_j3))

            if d_j3 == 0:
                last_j3_cmd = None

            if d_j3 != 0 and pos:
                j3_cur = int(pos['joint3'])
                j3_new = j3_cur + d_j3
                # j3_new = max(-90, min(90, j3_new))
                if last_j3_cmd is None or j3_new != last_j3_cmd:
                    arm.move_joint(3, j3_new)
                    last_j3_cmd = j3_new

            print(
                f"ARM({int(ax)},{int(ay)},{int(az)}) → TARGET({int(tx)},{int(ty)},{int(tz)}) | "
                f"dx:{int(dx)} dy:{int(dy)} dz:{int(dz)} | dJ1:{d_j1} dJ2:{d_j2} dJ3:{d_j3}"
            )

    cv2.imshow("ArUco solvePnP (mm)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
