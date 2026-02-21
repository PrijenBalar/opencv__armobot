import serial
import time

PORT = "COM15"      # Change to your port
BAUD = 1200000       # Change if needed

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    print(f"Listening on {PORT} @ {BAUD}...\n")

    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)

            # Decode to readable text
            text = data.decode("utf-8", errors="ignore")

            print("TEXT:", text)
            print("-" * 40)

        time.sleep(0.05)

except Exception as e:
    print("Error:", e)
