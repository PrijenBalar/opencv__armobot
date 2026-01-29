import serial
import time

print("Opening COM6...")

ser = serial.Serial('COM6', 9600, timeout=1)
time.sleep(2)   # Arduino reset time

print("COM6 opened successfully")

while True:
    ser.write(b'90,90\n')
    time.sleep(1)
