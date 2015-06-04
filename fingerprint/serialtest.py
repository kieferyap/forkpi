import serial
ser = serial.Serial("/dev/ttyAMA0")
read = ser.read()
print read
ser.close()