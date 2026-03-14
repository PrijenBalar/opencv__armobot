import serial
import struct

ser = serial.Serial(
    port='COM15',   # your telemetry COM port
    baudrate=57600,
    timeout=1
)

print("Listening to telemetry...")

while True:

    # search for header
    b = ser.read(1)
    if b != b'\xAA':
        continue

    if ser.read(1) != b'\x55':
        continue

    # read rest of packet
    payload = ser.read(9)

    if len(payload) != 9:
        continue

    ch1, ch2, ch3, ch4 = struct.unpack('<HHHH', payload[:8])
    crc = payload[8]

    # calculate crc
    calc_crc = 0
    for byte in payload[:8]:
        calc_crc ^= byte

    if crc == calc_crc:
        print(f"CH1:{ch1}  CH2:{ch2}  CH3:{ch3}  CH4:{ch4}")
    else:
        print("CRC error")