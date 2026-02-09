from onvif import ONVIFCamera
import time

# ================= CAMERA CONFIG =================
IP = "192.168.1.6"
PORT = 8888                 # ✅ ONVIF PORT (NOT 554, NOT 8888)
USER = "admin"
PASS = ""    # ❗ MUST NOT BE EMPTY

# ================= CONNECT =================
print("Connecting to ONVIF camera...")

cam = ONVIFCamera(IP, PORT, USER, PASS)

media = cam.create_media_service()
ptz = cam.create_ptz_service()

profiles = media.GetProfiles()

# Select profile that supports PTZ
profile = None
for p in profiles:
    if p.PTZConfiguration is not None:
        profile = p
        break

if profile is None:
    raise Exception("❌ No PTZ-enabled ONVIF profile found")

print("✅ ONVIF CONNECTED")
print("Profile token:", profile.token)

# ================= PTZ MOVE FUNCTION =================
def move_ptz(pan=0.0, tilt=0.0, zoom=0.0, duration=0.3):
    req = ptz.create_type("ContinuousMove")
    req.ProfileToken = profile.token
    req.Velocity = {
        "PanTilt": {"x": pan, "y": tilt},
        "Zoom": {"x": zoom}
    }

    ptz.ContinuousMove(req)
    time.sleep(duration)
    ptz.Stop({"ProfileToken": profile.token})

# ================= TEST MOVES =================
print("Testing PTZ movement...")

print("Pan Left")
move_ptz(pan=-0.5)

print("Pan Right")
move_ptz(pan=0.5)

print("Tilt Up")
move_ptz(tilt=0.5)

print("Tilt Down")
move_ptz(tilt=-0.5)

print("Zoom In")
move_ptz(zoom=0.5)

print("Zoom Out")
move_ptz(zoom=-0.5)

# ================= KEYBOARD CONTROL =================
print("\nPTZ MANUAL CONTROL")
print("W = Up | S = Down | A = Left | D = Right")
print("Q = Zoom In | E = Zoom Out | X = Exit\n")

while True:
    key = input("Command: ").lower().strip()

    if key == "a":
        move_ptz(pan=-0.4)
    elif key == "d":
        move_ptz(pan=0.4)
    elif key == "w":
        move_ptz(tilt=0.4)
    elif key == "s":
        move_ptz(tilt=-0.4)
    elif key == "q":
        move_ptz(zoom=0.4)
    elif key == "e":
        move_ptz(zoom=-0.4)
    elif key == "x":
        print("Exiting...")
        break
    else:
        print("Invalid key")
