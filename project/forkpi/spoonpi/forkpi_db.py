import psycopg2
from aes import AES
import hashlib

class ForkpiDB(object):

    def __init__(self):
        self.conn = psycopg2.connect(database="forkpi", user="pi", password="raspberry", host="forkpi.local", port="5432")
        self.conn.autocommit = True

    '''
    def encrypt(self, plaintext, name):
        cipher = AES(name)
        return cipher.encrypt(ciphertext)

    def decrypt(self, ciphertext, name):
        cipher = AES(name)
        return cipher.decrypt(ciphertext)

    def find_pins_for(self, rfid_uid):
        c = self.conn.cursor()
        c.execute("SELECT name, pin FROM records_keypair WHERE rfid_uid = '%s' AND is_active=TRUE" % rfid_uid)
        result = c.fetchall()
        result = map(lambda x: x[1], result)
        return result
    '''

    def hash_keypair(self, pin, rfid_uid):
        return hashlib.sha1((pin + rfid_uid).encode()).hexdigest()

    def authorize(self, pin, rfid_uid):
        '''
        Returns (is_authorized, names)
          is_authorized is True if there is an entry in the database
          names is the comma-separated string of the name/s corresponding to the keypair entered
            This is an empty string if is_authorized is False
        '''
        c = self.conn.cursor()
        hashpass = self.hash_keypair(pin, rfid_uid)
        c.execute("SELECT name FROM records_keypair WHERE hashpass = '%s' AND is_active=TRUE" % hashpass)
        result = c.fetchall()
        is_authorized = (len(result) > 0)
        names = ', '.join(map(lambda x: x[0], result))
        return is_authorized, names

    def log_allowed(self, names, pin='', rfid_uid=''):
        self.log("Allowed", details=names, pin=pin, rfid_uid=rfid_uid)

    def log_denied(self, reason, pin='', rfid_uid=''):
        self.log("Denied", details=reason, pin=pin, rfid_uid=rfid_uid)

    def log(self, action, details='', pin='', rfid_uid=''):
        c = self.conn.cursor()
        c.execute("INSERT INTO records_log(created_on, action, details, pin, rfid_uid) \
                     VALUES (now(), '%s', '%s', '%s', '%s')" % (action, details, pin, rfid_uid))

    def fetch_option(self, name):
        c = self.conn.cursor()
        c.execute("SELECT value, \"default\" FROM records_option WHERE name = '%s'" % name)
        result = c.fetchone()
        return result[0], result[1]
