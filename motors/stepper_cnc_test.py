import serial
import time

SERIAL_PORT = "/dev/cu.usbserial-110" # skal måske ændres alt efter computer, men det er hvor arduino er på
#TODO til nr 2 arduino kald enten SERIAL_PORT 2 osv


BAUD_RATE = 115200

# Connect til arduino
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2) 
ser.flushInput()

# Drej motor mod ur G - movement kode, X/Y/Z er position aka hvilken motor. F er speed
ser.write(b"G1 X10 F100\n")
time.sleep(0.5)
ser.write(b"G1 Y10 F100\n")
time.sleep(0.5)
ser.write(b"G1 Z10 F100\n")

#samme med uret
time.sleep(2)
ser.write(b"G1 X-10 F100\n")
time.sleep(0.5)
ser.write(b"G1 Y-10 F100\n")
time.sleep(0.5)
ser.write(b"G1 Z-10 F100\n")
time.sleep(0.5)


while ser.in_waiting:
    print(ser.readline().decode().strip())

ser.close()





