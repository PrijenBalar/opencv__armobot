import serial
import time

ser = serial.Serial('COM6', 9600, timeout=1)
time.sleep(2)  # allow Arduino reset

print("Sending angles... Press CTRL+C to stop")

pan = 90
tilt = 90

try:
    while True:
        ser.write(f"{pan},{tilt}\n".encode())
        print(f"Sent: {pan},{tilt}")

        pan += 5
        if pan > 270:
            pan = 40

        tilt += 5
        if tilt > 270:
            tilt = 40

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    ser.close()
    print("COM6 released")
