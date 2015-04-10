import threading
import binascii

from .fingerprint_scanner import FingerprintScanner

class FingerprintThread(threading.Thread):

    def __init__(self, ForkpiDB):
        super(FingerprintThread, self).__init__()
        print('Loading Fingerprint Reader...')
        self.fps = FingerprintScanner(debug=False)

        self.db = ForkpiDB()
        self.matches = [] # Keypair IDs whose fingerprint field matches the current finger
        self.is_polling = True
        self.is_found = False # True if a match was found

    def run(self):
        while True:
            while self.is_polling and not self.is_found:
                template = self.fps.make_template(blocking=True)
                self._print('Found a new finger!')
                self.fps.delete_template(_id=0)
                self.fps.upload_template(_id=0, template=template)

                self.matches = []
                match_found = False
                # fetch templates for this door from the forkpi db
                for _id, template in self.db.fetch_templates():
                    # verify all templates against id=0
                    template = binascii.unhexlify(bytes(template, 'utf-8'))
                    if self.fps.verify_template(_id=0, template=template):
                        self._print('Match with id %s' % _id)
                        # if template matches, add to list of keypair ids
                        self.matches.append(_id)
                        match_found = True
                if not match_found:
                    self._print('No match found.')
                # We set the flag to true only after we finish verifying against all the fingerprints
                self.is_found = match_found

    def _print(self, *args):
        print('  [FingerThread]', *args)