import psycopg2
from aes import AES

def connect_to_db():
    return psycopg2.connect(database="forkpi", user="pi", password="raspberry", host="forkpi.local", port="5432")

def encrypt(plaintext, name):
    cipher = AES(name)
    return cipher.encrypt(ciphertext)

def decrypt(ciphertext, name):
    cipher = AES(name)
    return cipher.decrypt(ciphertext)

def find_pins_for(rfid_uid):
    conn = connect_to_db()
    c = conn.cursor()
    c.execute("SELECT name, pin FROM records_keypair WHERE rfid_uid = '%s' AND is_active=TRUE" % rfid_uid)
    result = c.fetchall()
    result = map(lambda x: x[1], result)
    conn.close()
    return result

def log_allowed(pin='', rfid_uid=''):
    log("Allowed", pin=pin, rfid_uid=rfid_uid)

def log_denied(reason, pin='', rfid_uid=''):
    log("Denied", details=reason, pin=pin, rfid_uid=rfid_uid)

def log(action, details='', pin='', rfid_uid=''):
    conn = connect_to_db()
    c = conn.cursor()
    c.execute("INSERT INTO records_log(created_on, action, details, pin, rfid_uid) \
               VALUES (now(), '%s', '%s', '%s', '%s')" % (action, details, pin, rfid_uid))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print find_pins_for("83bd1fd0")
