from keypad import Keypad
from oled import OLED
from nfc_reader import NFCReader
from forkpi_db import find_pins_for

import time

led = OLED()
nfc_reader = NFCReader()
keypad = Keypad()

while True:
	led.clear_display()
	led.puts("Swipe RFID")
	uid = nfc_reader.read_tag()
	correct_pins = find_pins_for(uid)

	if len(correct_pins) != 0:
		pin_length = 4
		pin = ""
		led.clear_display()
		led.puts("Enter PIN:\n")

		while len(pin) < pin_length:
		    key = keypad.getch(timeout=5)
		    if key == Keypad.TIMEOUT:
		    	break
		    elif len(pin) == 0 and key == 0:
		    	print "First digit must not be zero."
		    elif Keypad.is_numeric(key):
		        pin += str(key)
		        led.puts("*")

		led.clear_display()
		if pin in correct_pins:
			print "Allowed UID({}) PIN({})".format(uid, pin)
			led.puts("Access\ngranted")
		elif key == Keypad.TIMEOUT:
			print "Denied  UID({}) PIN({}) : timeout".format(uid, pin)
			led.puts("Timeout")
		else:
			print "Denied  UID({}) PIN({}) : wrong pin".format(uid, pin)
			led.puts("Access\ndenied")
	else:
		led.clear_display()
		print "Denied  UID({}) : unrecognized uid".format(uid)
		led.puts("Access\ndenied")

	time.sleep(3)