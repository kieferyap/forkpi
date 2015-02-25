from keypad import Keypad
from oled import OLED
from nfc_reader import NFCReader
from forkpi_db import find_pins_for, log_allowed, log_denied

import time

class SpoonPi:
	# LOCKOUT TABLE columns [rfid_uid, incorrect_streak, lockout]
	COL_UID, COL_STREAK, COL_TIME_LEFT = range(3)

	def __init__(self):
		self.led = OLED()
		self.nfc_reader = NFCReader()
		self.keypad = Keypad()
		self.pin_length = 4
		self.attempt_limit = 2
		self.lockout_time =  30 # 30 minutes
		self.keypad_timeout = 5
		self.lockout_table = list()

	def allow_access(self, rfid_uid, pin):
		message = "Allowed UID({}) PIN({})".format(rfid_uid, pin)
		print message
		log_allowed(rfid_uid=rfid_uid, pin=pin)
		self.led.clear_display()
		self.led.puts("Access\ngranted")

	def deny_access(self, rfid_uid, pin, reason, led_message="Access\ndenied"):
		message = "Denied  UID({}) PIN({}) : {}".format(rfid_uid, pin, reason)
		print message
		log_denied(rfid_uid=rfid_uid, pin=pin, reason=reason)
		self.led.clear_display()
		self.led.puts(led_message)

	def rfid_authentication(self):
		self.led.clear_display()
		self.led.puts("Swipe RFID")
		rfid_uid = self.nfc_reader.read_tag()
		correct_pins = find_pins_for(rfid_uid)
		return rfid_uid, correct_pins

	def pin_authentication(self):
		pin = ""
		self.led.clear_display()
		self.led.puts("Enter PIN:\n")

		while len(pin) < self.pin_length:
		    key = self.keypad.getch(timeout=self.keypad_timeout)
		    if key == Keypad.TIMEOUT:
		    	break
		    #elif len(pin) == 0 and key == 0:
		    #	print "First digit must not be zero."
		    elif Keypad.is_numeric(key):
		        pin += str(key)
		        self.led.puts("*")
		return pin, key == Keypad.TIMEOUT

	def find_lockout_row(self, rfid_uid):
		lockout_row = None
		for row in self.lockout_table:
			if row[0] == rfid_uid:
				lockout_row = row
		if lockout_row is None:
			lockout_row = [rfid_uid, 0, 0]
			self.lockout_table.append(lockout_row)
		return lockout_row

	def update_lockout_timers(self, time_elapsed):
		for row in self.lockout_table:
			lockout_time_left = row[SpoonPi.COL_TIME_LEFT]
			was_locked_out = (lockout_time_left > 0)
			row[SpoonPi.COL_TIME_LEFT] = max(0, lockout_time_left - time_elapsed)
			if was_locked_out and row[SpoonPi.COL_TIME_LEFT] == 0:
				row[SpoonPi.COL_STREAK] = 0

	def run(self):
		while True:
			time_started = time.time()
			rfid_uid, correct_pins = self.rfid_authentication()

			if '' in correct_pins:
				self.allow_access(rfid_uid, '')

			elif len(correct_pins) != 0:
				lockout_row = self.find_lockout_row(rfid_uid)

				if lockout_row[SpoonPi.COL_TIME_LEFT] > 0:
					self.deny_access(rfid_uid, pin, reason="locked out", led_message="Locked out\nfor %ss" % lockout_row[SpoonPi.COL_TIME_LEFT])
				else:
					pin, timed_out = self.pin_authentication()
					is_authenticated = True
					
					if pin in correct_pins:
						self.allow_access(rfid_uid, pin)
					elif timed_out:
						self.deny_access(rfid_uid, pin, reason="timeout", led_message="Timeout")
						is_authenticated = False
					else:
						self.deny_access(rfid_uid, pin, reason="wrong pin")
						is_authenticated = False

					if is_authenticated:
						lockout_row[SpoonPi.COL_STREAK] = 0
						lockout_row[SpoonPi.COL_TIME_LEFT] = 0
					else:
						lockout_row[SpoonPi.COL_STREAK] += 1
						if lockout_row[SpoonPi.COL_STREAK] >= self.attempt_limit:
							time_elapsed = int(time.time() - time_started)
							lockout_row[SpoonPi.COL_TIME_LEFT] = self.lockout_time + time_elapsed
			else:
				self.deny_access(rfid_uid, pin="", reason="unrecognized rfid uid")

			time.sleep(2)
			time_elapsed = int(time.time() - time_started)
			self.update_lockout_timers(time_elapsed)
			# print self.lockout_table

if __name__ == '__main__':
	SpoonPi().run()