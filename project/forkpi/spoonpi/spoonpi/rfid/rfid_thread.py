import threading
from .rfid_reader import RfidReader

class RfidThread(threading.Thread):

    def __init__(self):
        super(RfidThread, self).__init__()
        self.rfid_reader = RfidReader()       # The RFID Reader
        self.reset()

    def reset(self):
        self.is_polling = False
        self.is_found = False # True if an RFID has been swiped
        self.rfid_uid = '' # The UID of the newly swiped RFID

    def start_polling(self):
        self.is_polling = True

    def run(self):
        while True:
            while self.is_polling and not self.is_found:
                self.rfid_uid = self.rfid_reader.read_tag()
                self._print("Found a new UID:", self.rfid_uid)
                self.is_found = True

    def _print(self, *args):
        print('  [RFIDThread]', *args)