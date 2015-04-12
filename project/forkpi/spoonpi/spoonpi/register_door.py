import sys
import psycopg2
from pi_serial import get_serial

def register_door(serial_num, door_name):
    conn = psycopg2.connect(database="forkpi", user="pi", password="raspberry", host="forkpi.local", port="5432")
    c = conn.cursor()

    c.execute("SELECT id FROM records_door WHERE name='%s' AND serial != '%s'"% (door_name, serial_num))
    result = c.fetchone()
    if result:
        print("The name '%s' is already taken. Please choose another name." % door_name)
    else:
        c.execute("SELECT id, name FROM records_door WHERE serial='%s'" % serial_num)
        result = c.fetchone()
        if result:
            c.execute("UPDATE records_door SET name='%s' WHERE id=%s" % (door_name, result[0]))
            conn.commit()
            print("Changed name from '%s' to '%s'!" % (result[1], door_name))
        else:
            c.execute("INSERT INTO records_door(name, serial) VALUES ('%s', '%s')" % (door_name, serial_num))
            conn.commit()
            print("Successfully registered as '%s'!" % door_name)
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python3 %s <door name>' % sys.argv[0])
    else:
        door_name = ' '.join(sys.argv[1:]).replace('\'', '').replace('\n', '')
        serial_num = get_serial()
        if serial_num:
            register_door(serial_num, door_name)
        else:
            print('Unable to get serial number!')
