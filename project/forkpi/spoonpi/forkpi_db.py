import sqlite3

def find_by_rfid_uid(rfid_uid):
	conn = sqlite3.connect('../db.sqlite3')
	with conn:
		c = conn.cursor()
		c.execute("SELECT name, pin FROM records_kiefers WHERE rfid_uid = '%s'" % rfid_uid)
		result = c.fetchall()
		return result


def find_pins_for(rfid_uid):	
	conn = sqlite3.connect('../db.sqlite3')
	with conn:
		c = conn.cursor()
		c.execute("SELECT pin FROM records_kiefers WHERE rfid_uid = '%s'" % rfid_uid)
		result = c.fetchall()
		result = map(lambda x: x[0], result)
		return result

if __name__ == '__main__':
	print find_pins_for("83bd1fd0")