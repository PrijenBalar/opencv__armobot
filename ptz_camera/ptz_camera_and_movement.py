from onvif import ONVIFCamera
import cv2
import time

# ================= CAMERA CONFIG =================
IP = "192.168.1.26"
ONVIF_PORT = 8888
USER = "admin"
PASS = ""   # Put password if camera has one

RTSP_URL = "rtsp://admin:@192.168.1.26:554/ch0_0.264"

# ================= CONNECT TO ONVIF =================
print("Connecting to ONVIF camera...")

cam = ONVIFCamera(IP, ONVIF_PORT, USER, PASS)

media = cam.create_media_service()
ptz = cam.create_ptz_service()
profiles = media.GetProfiles()

profile = None
for p in profiles:
    if p.PTZConfiguration is not None:
        profile = p
        break

if profile is None:
    raise Exception("No PTZ-enabled profile found")

print("ONVIF Connected Successfully")
print("Profile Token:", profile.token)

# ================= PTZ FUNCTIONS =================
def move_ptz(pan=0.0, tilt=0.0, zoom=0.0):
    req = ptz.create_type("ContinuousMove")
    req.ProfileToken = profile.token
    req.Velocity = {
        "PanTilt": {"x": pan, "y": tilt},
        "Zoom": {"x": zoom}
    }
    ptz.ContinuousMove(req)

def stop_ptz():
    ptz.Stop({"ProfileToken": profile.token})

# ================= OPEN RTSP VIDEO =================
print("Opening RTSP stream...")

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("RTSP stream not opened")
    exit()

print("Video Started Successfully")

# ================= PRINT CONTROLS =================
print("\n========== PTZ KEY CONTROLS ==========")
print("W  -> Tilt Up")
print("S  -> Tilt Down")
print("A  -> Pan Left")
print("D  -> Pan Right")
print("Q  -> Zoom In")
print("E  -> Zoom Out")
print("SPACE -> Stop Movement")
print("ESC -> Exit Program")
print("======================================\n")

# ================= MAIN LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame not received")
        break

    frame = cv2.resize(frame, (640, 480))
    cv2.imshow("PTZ Camera Control", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('w'):
        print("Tilt Up")
        move_ptz(tilt=0.5)

    elif key == ord('s'):
        print("Tilt Down")
        move_ptz(tilt=-0.5)

    elif key == ord('a'):
        print("Pan Left")
        move_ptz(pan=-0.5)

    elif key == ord('d'):
        print("Pan Right")
        move_ptz(pan=0.5)

    elif key == ord('q'):
        print("Zoom In")
        move_ptz(zoom=0.5)

    elif key == ord('e'):
        print("Zoom Out")
        move_ptz(zoom=-0.5)

    elif key == 32:  # SPACE
        print("Stop Movement")
        stop_ptz()

    elif key == 27:  # ESC
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
