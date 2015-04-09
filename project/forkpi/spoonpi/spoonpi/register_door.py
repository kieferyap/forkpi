import sys
import psycopg2
from pi_serial import get_serial

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 %s <door name>' % sys.argv[0])
    else:
        serial_num = get_serial()

        conn = psycopg2.connect(database="forkpi", user="pi", password="raspberry", host="forkpi.local", port="5432")
        c = conn.cursor()

        c.execute("SELECT name FROM records_door WHERE serial='%s'" % serial_num)
        result = c.fetchone()
        if result:
            print('ERROR: Already registered as %s!' % result[0])
        else:
            door_name = sys.argv[1]
            c.execute("INSERT INTO records_door(name, serial) VALUES ('%s', '%s')" % (door_name, serial_num))
            conn.commit()
            print('Successfully registered as %s!' % door_name)
        conn.close()
