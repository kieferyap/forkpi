from keypad import Keypad
from oled import OLED
from nfc_reader import NFCReader
import time

led = OLED()
nfc_reader = NFCReader()
keypad = Keypad()

correct_uid = "83bd1fd0"
correct_pin = "1234"

while True:
	led.clear_display()
	led.puts("Swipe RFID")
	uid = nfc_reader.read_tag()
	print "Found uid:", uid

	if uid == correct_uid:
		pin_length = 4
		pin = ""
		led.clear_display()
		led.puts("Enter PIN:\n")

		while len(pin) < pin_length:
		    key = keypad.getch(timeout=5)
		    if key == Keypad.TIMEOUT:
		    	print "Timeout!"
		    	break
		    elif len(pin) == 0 and key == 0:
		    	print "First digit must not be zero."
		    elif Keypad.is_numeric(key):
		        pin += str(key)
		        led.puts("*")

		led.clear_display()
		if pin == correct_pin:
			led.puts("Access\ngranted")
		else:
			led.puts("Access\ndenied")

		print pin
	else:
		led.clear_display()
		led.puts("Access\ndenied")

	time.sleep(3)

	print "Finished a transaction"