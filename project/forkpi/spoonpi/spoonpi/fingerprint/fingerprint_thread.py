import time
import threading
import binascii

from .fingerprint_scanner import FingerprintScanner

class FingerprintThread(threading.Thread):

    def __init__(self, ForkpiDB):
        super(FingerprintThread, self).__init__()
        self.fps = FingerprintScanner(debug=False)
        self.db = ForkpiDB()
        self.template = None # The template of the newly scanned finger
        self.matches = [] # Keypair IDs whose fingerprint field matches the current finger

    def start_polling(self):
        self.is_polling = True
        self.finger_scanned = False # True if a finger has been scanned (not necessarily match)

    def stop_polling(self):
        self.is_polling = False

    def run(self):
        self.start_polling()
        while True:
            while self.is_polling and not self.finger_scanned:
                try:
                    self.template = self.fps.make_template(tries=1)
                    if self.template:
                        self.fps.backlight_off()

                        self.fps.delete_template(_id=0)
                        self.fps.upload_template(_id=0, template=self.template)

                        self.matches = []
                        match_found = False
                        # fetch templates for this door from the forkpi db
                        for _id, template in self.db.fetch_templates():
                            # verify all templates against id=0
                            if len(template) == 996:
                                try:
                                    template = binascii.unhexlify(bytes(template, 'utf-8'))
                                except Exception:
                                    pass
                                else:
                                    if self.fps.verify_template(_id=0, template=template):
                                        self._print('Match with id %s' % _id)
                                        # if template matches, add to list of keypair ids
                                        self.matches.append(_id)
                                        match_found = True
                        
                        if not match_found:
                            self._print('No match found.')
                            # This is so that the query for keypairs matching this fingerprint will return nothing
                            self.matches = [-1]

                        self.finger_scanned = True

                except Exception:
                    self.fps = FingerprintScanner(debug=False)
            time.sleep(0.5)

    def _print(self, *args):
        print('  [FingerThread]', *args)

    def get_matches(self):
        self.finger_scanned = False
        return self.matches