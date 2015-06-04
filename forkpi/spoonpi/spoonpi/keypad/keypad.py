import RPi.GPIO as GPIO
import traceback
import time

class Keypad:

    MATRIX = [ ['1', '2', '3' ],
               ['4', '5', '6' ],
               ['7', '8', '9' ],
               ['*', '0', '#' ] ]

    # GPIO pin numbers
    ROWS = [7, 11, 13, 15]
    COLS = [12, 16, 18]

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

    def getch(self, timeout=None):
        for col in Keypad.COLS:
            GPIO.setup(col, GPIO.OUT)
            GPIO.output(col, 1)

        for row in Keypad.ROWS:
            GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        try:
            time_started = time.mktime(time.gmtime())
            while(True):
                current_time = time.mktime(time.gmtime()) 
                if timeout is not None:
                    if current_time > time_started + timeout:
                        return None

                for j, col in enumerate(Keypad.COLS):
                    GPIO.output(col, 0)
                    
                    for i, row in enumerate(Keypad.ROWS):
                        if GPIO.input(row) == 0:
                            key =  Keypad.MATRIX[i][j]
                            time.sleep(0.3)
                            while(GPIO.input(row) == 0):
                                pass
                            return key
                    GPIO.output(col, 1)
        except Exception as err:
            print(traceback.format_exc())
            GPIO.cleanup()