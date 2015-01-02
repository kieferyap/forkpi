import sqlite3
from aes import AES

def encrypt(plaintext, name):
    cipher = AES(name)
    return cipher.encrypt(ciphertext)

def decrypt(ciphertext, name):
    cipher = AES(name)
    return cipher.decrypt(ciphertext)

def find_pins_for(rfid_uid):
    conn = sqlite3.connect('../db.sqlite3')
    conn.create_function("decrypt", 2, decrypt)
    with conn:
        c = conn.cursor()
        c.execute("CREATE TEMPORARY TABLE decrypted_kiefers(name, pin, rfid_uid, decrypted_rfid_uid)")
        c.execute("INSERT INTO decrypted_kiefers SELECT name, pin, rfid_uid, decrypt(rfid_uid, name) FROM records_kiefers")
        c.execute("SELECT decrypt(pin,name) FROM decrypted_kiefers WHERE decrypted_rfid_uid = '%s'" % rfid_uid)
        result = c.fetchall()
        result = map(lambda x: x[0], result)
        c.execute("DROP TABLE decrypted_kiefers")
        return result

def log(message):
    conn = sqlite3.connect('../db.sqlite3')
    with conn:
        c = conn.cursor()
        c.execute("DELETE FROM records_logs WHERE julianday('now') - julianday(created_on) > 30")
        c.execute("INSERT INTO records_logs (created_on, text) VALUES (datetime(), '%s')" % message)

def delete_logs():
    conn = sqlite3.connect('../db.sqlite3')
    with conn:
        c = conn.cursor()
        c.execute("DELETE FROM records_logs WHERE julianday('now') - julianday(created_on) > 30")


if __name__ == '__main__':
    print find_pins_for("83bd1fd0")