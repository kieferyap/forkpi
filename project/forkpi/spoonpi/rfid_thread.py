import threading
from nfc_reader import NFCReader

class RfidThread(threading.Thread):

	def __init__(self):
		super(RfidThread, self).__init__()
		print('Loading NFC Reader...')
		self.rfid_uid = ''					# The UID of the newly swiped RFID
		self.is_found = False				# Has a new RFID been swiped?
		self.nfc_reader = NFCReader()		# The NFC Reader

	def run(self):
		while True:
			while not self.is_found:
				self.rfid_uid = self.nfc_reader.read_tag()
				print("[RFIDThread]: Found a new UID:", self.rfid_uid)
				self.is_found = True