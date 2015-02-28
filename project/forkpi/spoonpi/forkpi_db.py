import psycopg2
from aes import AES

class ForkpiDB(object):

    def __init__(self):
        self.conn = psycopg2.connect(database="forkpi", user="pi", password="raspberry", host="forkpi.local", port="5432")
        self.conn.autocommit = True

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

    def log_allowed(self, pin='', rfid_uid=''):
        self.log("Allowed", pin=pin, rfid_uid=rfid_uid)

    def log_denied(self, reason, pin='', rfid_uid=''):
        self.log("Denied", details=reason, pin=pin, rfid_uid=rfid_uid)

    def log(self, action, details='', pin='', rfid_uid=''):
        c = self.conn.cursor()
        c.execute("INSERT INTO records_log(created_on, action, details, pin, rfid_uid) \
                   VALUES (now(), '%s', '%s', '%s', '%s')" % (action, details, pin, rfid_uid))

    def fetch_option(self, name):
        c = self.conn.cursor()
        c.execute("SELECT value FROM records_option WHERE name = '%s'" % name)
        result = c.fetchone()[0]
        return result


if __name__ == '__main__':
    print ForkpiDB().find_pins_for("83bd1fd0")
