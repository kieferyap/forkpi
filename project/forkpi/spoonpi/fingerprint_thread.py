import threading
from nfc_reader import NFCReader

class FingerprintThread(threading.Thread):

	def __init__(self):
		super(FingerprintThread, self).__init__()
		print('Loading Fingerprint Reader...')
		self.fps = FingerprintScanner(debug=True)	# The Fingerprint scanner
		self.finger_id = 0							# The ID of the newly swiped finger
		self.is_found = False						# Has a new finger been swiped?

	def run(self):
		while True:
			while not self.is_found:
				# Dummy algo:
				identify_id = self.fps.identify_finger(tries=50)
				if identify_id >= 0:
					print('Match with id %s' % identify_id)
					self.finger_id = identify_id
					self.is_found = True
				else:
					print('No match found')

				# Check if there's a newly-pressed finger
				# If there's a newly-pressed finger, upload the templates by the 200s