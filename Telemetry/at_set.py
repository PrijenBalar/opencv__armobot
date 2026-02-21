import serial
import time

PORT = "COM15"
CURRENT_BAUD = 1200000   # The baud where you got OK
NEW_BAUD_CODE = 460        # 7 = 57600

ser = serial.Serial(PORT, CURRENT_BAUD, timeout=2)

# Ensure silence
ser.reset_input_buffer()
ser.reset_output_buffer()
time.sleep(3)

# Enter AT mode
ser.write(b"+++")
time.sleep(2)

response = ser.read_all().decode(errors="ignore")
print("AT Response:", response)

if "OK" not in response:
    print("Failed to enter AT mode. STOP.")
    ser.close()
    exit()

# Set baud
ser.write(b"ATS1=460\r\n")
time.sleep(1)
print("Set Response:", ser.read_all().decode(errors="ignore"))

# Save settings
ser.write(b"AT&W\r\n")
time.sleep(1)
print("Save Response:", ser.read_all().decode(errors="ignore"))

# Reboot
ser.write(b"ATZ\r\n")
time.sleep(3)

ser.close()

print("\nNow reconnect at 57600 to verify...\n")

# Verify new baud
ser = serial.Serial(PORT, 57600, timeout=2)
time.sleep(2)

ser.write(b"+++")
time.sleep(2)

print("Verification:", ser.read_all().decode(errors="ignore"))

ser.close()
