import time
import threading

from .rfid_reader import RfidReader

class RfidThread(threading.Thread):

    def __init__(self):
        super(RfidThread, self).__init__()
        self.rfid_reader = RfidReader()
        self.rfid_uid = '' # The UID of the newly swiped RFID

    def start_polling(self):
        self.is_polling = True
        self.tag_swiped = False

    def stop_polling(self):
        self.is_polling = False

    def run(self):
        self.start_polling()
        while True:
            while self.is_polling and not self.tag_swiped:
                try:
                    self.rfid_uid = self.rfid_reader.read_tag(blocking=True)
                    if self.rfid_uid:
                        self._print("Found a new UID:", self.rfid_uid)
                        self.tag_swiped = True
                except Exception:
                    self.rfid_reader = RfidReader()
            time.sleep(0.5)

    def _print(self, *args):
        print('  [RFIDThread]', *args)

    def get_rfid_uid(self):
        self.tag_swiped = False
        return self.rfid_uid