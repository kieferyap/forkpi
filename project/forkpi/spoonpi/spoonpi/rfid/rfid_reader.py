try:
    from py532lib.mifare import Mifare
except ImportError:
    from .py532lib.mifare import Mifare

from binascii import hexlify

class RfidReader():

    def __init__(self):
        self.mifare = Mifare()
        self.mifare.SAMconfigure()

    def read_tag(self):
        rfid_uid = self.mifare.scan_field()
        return hexlify(rfid_uid).decode()