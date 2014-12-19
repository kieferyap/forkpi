import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

MATRIX =	[
				[1,	2, 3],
				[4,	5, 6],
				[7,	8, 9],
				['*', 0, '#']
			]

ROW = [7, 11, 13, 15]
COL = [12, 16, 18]

for j in range(3):
	GPIO.setup(COL[j], GPIO.OUT)
	GPIO.output(COL[j], 1)

for i in range(4):
	GPIO.setup(ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

try:
	while(True):
		for j in range(3):
			GPIO.output(COL[j], 0)
			
			for i in range(4):
				if GPIO.input(ROW[i]) == 0:
					print MATRIX[i][j]
					time.sleep(0.3)
					while(GPIO.input(ROW[i]) == 0):
						pass
			
			GPIO.output(COL[j], 1)

	
except:
	GPIO.cleanup()