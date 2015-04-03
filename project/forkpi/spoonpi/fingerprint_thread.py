import threading
from fingerprint import *

class FingerprintThread(threading.Thread):

	def __init__(self):
		super(FingerprintThread, self).__init__()
		print('Loading Fingerprint Reader...')
		self.fps = FingerprintScanner(debug=False)	# The Fingerprint scanner
		self.finger_id = 0							# The ID of the newly swiped finger
		self.is_not_polling = False					# A flag which sets polling
		self.is_found = False						# Has a new finger been swiped?

	def run(self):
		while True:
			# Backlight should be false if not polling.
			self.fps.set_backlight(False)

			# Poll for a finger.
			while not (self.is_found or self.is_not_polling):
				# Dummy algo:
				identify_id = self.fps.identify_finger(tries=1)
				if identify_id >= 0:
					print('Match with id %s' % identify_id)
					self.finger_id = identify_id
					self.fps.set_backlight(False)
					self.is_found = True
				else:
					print('No match found')

				# Legit algo:
				# Check if there's a newly-pressed finger
				# If there's a newly-pressed finger, upload the templates by the 200s and match
				# If there's a match, return the ID.