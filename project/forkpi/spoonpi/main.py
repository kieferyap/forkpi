from keypad import Keypad
from oled import OLED
from nfc_reader import NFCReader
from forkpi_db import ForkpiDB

import time
from math import ceil

class SpoonPi:
	# LOCKOUT TABLE columns [rfid_uid, incorrect_streak, lockout]
	COL_UID, COL_STREAK, COL_TIME_LEFT = list(range(3))

	def __init__(self):
		self.lockout_table = list()

		print('Loading OLED...')
		self.led = OLED()
		print('Loading NFC Reader...')
		self.nfc_reader = NFCReader()
		print('Loading keypad...')
		self.keypad = Keypad()
		print('Loading the ForkPi database...')
		self.db = ForkpiDB()
		print('Loading options...')
		self.attempt_limit = self.load_option('attempt_limit')
		self.lockout_time = self.load_option('lockout_time_minutes') * 60
		self.keypad_timeout = self.load_option('keypad_timeout_seconds')

	def load_option(self, name):
		value, default = self.db.fetch_option(name)
		if value.isdigit():
			print('  custom : {} = {}'.format(name, value))
			return int(value)
		else:
			print('  default: {} = {}'.format(name, default))
			return int(default)

	def allow_access(self, names, pin, rfid_uid):
		pin = '*' * len(pin) # convert pin to asterisks so pin is not exposed in the logs
		message = "Allowed PIN({}) UID({}) : {}".format(pin, rfid_uid, names)
		print(message)
		self.db.log_allowed(names=names, pin=pin, rfid_uid=rfid_uid)
		self.led.clear_display()
		self.led.puts("Access\ngranted")

	def deny_access(self, reason, pin, rfid_uid, led_message="Access\ndenied"):
		message = "Denied  PIN({}) UID({}) : {}".format(pin, rfid_uid, reason)
		print(message)
		self.db.log_denied(reason=reason, pin=pin, rfid_uid=rfid_uid)
		self.led.clear_display()
		self.led.puts(led_message)

	def rfid_authentication(self):
		self.led.clear_display()
		self.led.puts("Swipe RFID")
		rfid_uid = self.nfc_reader.read_tag()
		return rfid_uid

	def pin_authentication(self):
		'''
		Returns (pin, timeout) where
		  pin = the pin entered (string)
		  timeout = whether the keypad timed out (boolean)
		'''
		pin = ''
		self.led.clear_display()
		self.led.puts("Enter PIN:\n")

		while True:
		    key = self.keypad.getch(timeout=self.keypad_timeout)
		    if key == Keypad.TIMEOUT:
		    	return pin, True
		    elif key.isdigit():
		        pin += str(key)
		        self.led.puts('*')
		    elif key == '*': # backspace
		    	pin = pin[:-1]
		    	self.led.puts('\b')
		    elif key == '#': # enter
		    	return pin, False

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
			
			rfid_uid = self.rfid_authentication()

			time_elapsed = int(time.time() - time_started)
			self.update_lockout_timers(time_elapsed)

			time_started = time.time()
			
			is_authorized, names = self.db.authorize(pin='', rfid_uid=rfid_uid)
			if is_authorized:
				self.allow_access(names=names, pin='', rfid_uid=rfid_uid)
			else:
				lockout_row = self.find_lockout_row(rfid_uid)

				if lockout_row[SpoonPi.COL_TIME_LEFT] > 0:
					self.deny_access(reason="locked out", pin='', rfid_uid=rfid_uid,
						led_message="Locked out\nfor %sm" % int(ceil(lockout_row[SpoonPi.COL_TIME_LEFT] / 60.0)))
				else:
					pin, timed_out = self.pin_authentication()

					is_authenticated = True
					if timed_out:
						self.deny_access(reason="timeout", pin=pin, rfid_uid=rfid_uid, led_message="Timeout")
						is_authenticated = False
					else:
						is_authorized, names = self.db.authorize(pin=pin, rfid_uid=rfid_uid)
						if is_authorized:
							self.allow_access(names=names, pin=pin, rfid_uid=rfid_uid)
						else:
							self.deny_access(reason="wrong pin", pin=pin, rfid_uid=rfid_uid)
							is_authenticated = False

					if is_authenticated:
						lockout_row[SpoonPi.COL_STREAK] = 0
						lockout_row[SpoonPi.COL_TIME_LEFT] = 0
					else:
						lockout_row[SpoonPi.COL_STREAK] += 1
						if lockout_row[SpoonPi.COL_STREAK] >= self.attempt_limit:
							lockout_row[SpoonPi.COL_TIME_LEFT] = self.lockout_time

			time.sleep(2)
			time_elapsed = int(time.time() - time_started)
			self.update_lockout_timers(time_elapsed)
			# print self.lockout_table

if __name__ == '__main__':
	SpoonPi().run()