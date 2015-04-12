try:
    import py532lib.mifare as mifare
except ImportError:
    from .py532lib import mifare as mifare

from binascii import hexlify

class RfidReader():

    def __init__(self):
        self.mifare = mifare.Mifare()
        self.mifare.SAMconfigure()

    def read_tag(self, blocking=True):
        if blocking:
            self.mifare.set_max_retries(mifare.MIFARE_WAIT_FOR_ENTRY)
        else:
            self.mifare.set_max_retries(mifare.MIFARE_SAFE_RETRIES)

        rfid_uid = self.mifare.scan_field()
        if rfid_uid:
            return hexlify(rfid_uid).decode()
        else:
            return None