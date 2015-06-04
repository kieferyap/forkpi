import psycopg2
import hashlib
from pi_serial import get_serial

class ForkpiDB(object):

    def __init__(self):
        self.conn = psycopg2.connect(database="forkpi", user="pi", password="raspberry", host="forkpi.local", port="5432")
        self.conn.autocommit = True
        self.door_id = self.fetch_door_id()

    def hash_string(self, value):
        return hashlib.sha1((value).encode()).hexdigest()

    def authenticate(self, *args, **kwargs):
        '''
        Returns (is_authorized, names)
          is_authorized is True if there is an entry in the database
          names is the list of names that match the keypair conditions entered
             This is an empty list if is_authorized is False
        '''
        keywords = kwargs.keys()
        if len(keywords) != 2: # not two-factor (if single-factor, pin should be set to empty string)
            raise ValueError("Must provide exactly two of 'pin', 'rfid_uid', or 'fingerprint_matches")

        conditions = ['is_active = TRUE']
        
        if 'pin' in keywords:
            pin = kwargs['pin']
            conditions.append("hash_pin = '%s'" % self.hash_string(pin))
        if 'rfid_uid' in keywords:
            rfid_uid = kwargs['rfid_uid']
            conditions.append("hash_rfid = '%s'" % self.hash_string(rfid_uid))
        if 'fingerprint_matches' in keywords:
            keypair_ids = kwargs['fingerprint_matches']
            # (id=1 OR id=2 OR ...) if fingerprint matched with those ids
            conditions.append('(%s)' % ' OR '.join(map(lambda x: 'K.id='+str(x), keypair_ids)))
        
        conditions = ' AND '.join(conditions)

        c = self.conn.cursor()
        c.execute("SELECT name FROM records_keypair K JOIN records_keypair_doors KD ON (K.id=KD.keypair_id) WHERE KD.door_id=%s AND %s" % (self.door_id, conditions))
        result = c.fetchall()
        is_authorized = (len(result) > 0)
        names = [x[0] for x in result]
        return is_authorized, names

    def log_allowed(self, names, **kwargs):
        self.log(was_allowed=True, details=names, **kwargs)

    def log_denied(self, reason, **kwargs):
        self.log(was_allowed=False, details=reason, **kwargs)

    def log(self, was_allowed, details='', pin='', rfid_uid='', fingerprint_matches=[]):
        used_fingerprint = len(fingerprint_matches) > 0
        c = self.conn.cursor()
        c.execute("INSERT INTO records_log(created_on, door_id, was_allowed, details, pin, rfid_uid, used_fingerprint) \
                     VALUES (now(), %s, '%s', '%s', '%s', '%s', %s)" % (self.door_id, was_allowed, details, pin, rfid_uid, used_fingerprint))

    def fetch_option(self, name):
        c = self.conn.cursor()
        c.execute("SELECT value, \"default\" FROM records_option WHERE name = '%s'" % name)
        result = c.fetchone()
        return result[0], result[1]

    def fetch_door_id(self):
        serial_num = get_serial()
        if serial_num is None:
            raise Exception("Unable to get serial number!")

        c = self.conn.cursor()
        c.execute("SELECT id FROM records_door WHERE serial = '%s'" % serial_num)
        result = c.fetchone()
        if result:
            return result[0]
        else:
            raise Exception('Register this door with ForkPi first!')

    def fetch_templates(self):
        c = self.conn.cursor()
        # Fetch active keypairs that are mapped to this door and have a non-blank fingerprint_template field
        c.execute("""
            SELECT K.id, K.fingerprint_template
            FROM records_keypair K JOIN records_keypair_doors KD ON (K.id = KD.keypair_id)
            WHERE K.is_active = TRUE AND K.fingerprint_template != '' AND KD.door_id = %s """ % self.door_id);
        result = c.fetchall()
        return result