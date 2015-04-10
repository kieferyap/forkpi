import struct
import serial
import binascii
import time

def hexlify(_bytes):
    ''' Return hex representation of bytes '''
    # return ' '.join(binascii.hexlify(ch) for ch in _bytes)
    # return binascii.hexlify(_bytes)
    return ' '.join(["{0:0>2X}".format(b) for b in _bytes])

def byte_checksum(_bytes):
    ''' Sum of all bytes in string truncated to a byte '''
    return sum(_bytes) & 0xFFFF


class CommandPacket(object):

    START_CODE_1 = 0x55
    START_CODE_2 = 0xAA
    DEVICE_ID = 0x0001

    COMMANDS = {
        'Open'                : 0x01, # Open Initialization
        'Close'               : 0x02, # Close Termination
        'ChangeBaudrate'      : 0x04, # ChangeBaudrate Change UART baud rate
        'CmosLed'             : 0x12, # CmosLed Control CMOS LED
        'GetEnrollCount'      : 0x20, # Get enrolled fingerprint count
        'CheckEnrolled'       : 0x21, # Check whether the specified ID is already enrolled
        'EnrollStart'         : 0x22, # Start an enrollment
        'Enroll1'             : 0x23, # Make 1st template for an enrollment
        'Enroll2'             : 0x24, # Make 2nd template for an enrollment
        'Enroll3'             : 0x25, # Make 3rd template for an enrollment, merge three templates into one template, save merged template to the database
        'IsPressFinger'       : 0x26, # Check if a finger is placed on the sensor
        'DeleteID'            : 0x40, # Delete the fingerprint with the specified ID
        'DeleteAll'           : 0x41, # Delete all fingerprints from the database
        'Verify1_1'           : 0x50, # Verification of the capture fingerprint image with the specified ID
        'Identify1_N'         : 0x51, # Identification of the capture fingerprint image with the database
        'VerifyTemplate1_1'   : 0x52, # Verification of a fingerprint template with the specified ID
        'IdentifyTemplate1_N' : 0x53, # Identification of a fingerprint template with the database
        'CaptureFinger'       : 0x60, # Capture a fingerprint image(256x256) from the sensor
        'MakeTemplate'        : 0x61, # Make template for transmission
        'GetImage'            : 0x62, # Download the captured fingerprint image(256x256)
        'GetRawImage'         : 0x63, # Capture & Download raw fingerprint image(320x240)
        'GetTemplate'         : 0x70, # Download the template of the specified ID
        'SetTemplate'         : 0x71, # Upload the template of the specified ID
    }

    def __init__(self, command_name, parameter=0):
        if command_name in self.COMMANDS:
            self.name = command_name
            self.command_code = self.COMMANDS[command_name]
            self.parameter = parameter
        else:
            raise ValueError("%s not in command list" % command_name)

    def _pack_bytes(self, little_endian=True):
        if little_endian:
            byte_order = '<'
        else: # big endian
            byte_order = '>'

        _bytes = struct.pack(byte_order + 'BBHiH', # byte byte word dword word
                self.START_CODE_1, self.START_CODE_2, self.DEVICE_ID, self.parameter, self.command_code)
        checksum = byte_checksum(_bytes)
        _bytes += struct.pack(byte_order + 'H', checksum)
        return _bytes

    def serialize_bytes(self, little_endian=False):
        _bytes = self._pack_bytes(little_endian)
        return hexlify(_bytes)

    def __bytes__(self):
        return self._pack_bytes(little_endian=True)
        

class ResponsePacket(object):

    START_CODE_1 = 0x55
    START_CODE_2 = 0xAA
    DEVICE_ID = 0x0001

    ERRORS = {
        0x1001: 'NACK_TIMEOUT'              , # Obsolete, capture timeout
        0x1002: 'NACK_INVALID_BAUDRATE'     , # Obsolete, Invalid serial baud rate
        0x1003: 'NACK_INVALID_POS'          , # The specified ID is not between 0~199
        0x1004: 'NACK_IS_NOT_USED'          , # The specified ID is not used
        0x1005: 'NACK_IS_ALREADY_USED'      , # The specified ID is already used
        0x1006: 'NACK_COMM_ERR'             , # Communication Error
        0x1007: 'NACK_VERIFY_FAILED'        , # 1:1 Verification Failure
        0x1008: 'NACK_IDENTIFY_FAILED'      , # 1:N Identification Failure
        0x1009: 'NACK_DB_IS_FULL'           , # The database is full
        0x100A: 'NACK_DB_IS_EMPTY'          , # The database is empty
        0x100B: 'NACK_TURN_ERR'             , # Obsolete, Invalid order of the enrollment (The order was not as: EnrollStart -> Enroll1 -> Enroll2 -> Enroll3)
        0x100C: 'NACK_BAD_FINGER'           , # Too bad fingerprint
        0x100D: 'NACK_ENROLL_FAILED'        , # Enrollment Failure
        0x100E: 'NACK_IS_NOT_SUPPORTED'     , # The specified command is not supported
        0x100F: 'NACK_DEV_ERR'              , # Device Error, especially if Crypto-Chip is trouble
        0x1010: 'NACK_CAPTURE_CANCELED'     , # Obsolete, The capturing is canceled
        0x1011: 'NACK_INVALID_PARAM'        , # Invalid parameter
        0x1012: 'NACK_FINGER_IS_NOT_PRESSED', # Finger is not pressed          
    }

    def __init__(self, _bytes):
        self._bytes = _bytes
        self._unpack_bytes()

    def _unpack_bytes(self):
        values = struct.unpack('<BBHiHH', self._bytes) # byte byte word dword word word
        assert values[0] == self.START_CODE_1
        assert values[1] == self.START_CODE_2
        assert values[2] == self.DEVICE_ID
        response = values[4]
        checksum = values[5]
        assert checksum == byte_checksum(self._bytes[:-2])
        self.ack = True if response == 0x30 else False
        if self.ack:
            self.parameter = values[3]
        else:
            self.error_code = values[3]
            self.error = self.ERRORS.get(self.error_code, "DUPLICATE_ID_" + str(self.error_code))

    def __bytes__(self):
        return self._bytes

    def __bool__(self):
        return self.ack

    def serialize_bytes(self, little_endian=False):
        ''' Return hex representation of bytes '''
        if little_endian:
            _bytes = self._bytes
        else:
            values = struct.unpack('<BBHiHH', self._bytes) # byte byte word dword word word
            _bytes = struct.pack('>BBHiHH', *values)
        return hexlify(_bytes)


class DataPacket(object):

    START_CODE_1 = 0x5A
    START_CODE_2 = 0xA5
    DEVICE_ID = 0x0001

    def __init__(self, _bytes=None, data=None):
        assert not (_bytes and data)
        if _bytes: # unpack data from bytes
            self._bytes = _bytes
            self.data_length = len(_bytes) - 6
            self._unpack_bytes()
        elif data: # pack data to bytes
            self.data = bytes(data)
            self.data_length = len(self.data)
            self._pack_bytes()

    def _pack_bytes(self, little_endian=True):
        if little_endian:
            byte_order = '<'
        else: # big endian
            byte_order = '>'

        _bytes = struct.pack(byte_order + 'BBH%ds' % self.data_length, # byte byte word dword word
                self.START_CODE_1, self.START_CODE_2, self.DEVICE_ID, self.data)
        checksum = byte_checksum(_bytes)
        _bytes += struct.pack(byte_order + 'H', checksum)
        self._bytes = _bytes
        return self._bytes

    def _unpack_bytes(self):
        values = struct.unpack('<BBH%dsH' % self.data_length, self._bytes) # byte byte word var word
        assert values[0] == self.START_CODE_1
        assert values[1] == self.START_CODE_2
        assert values[2] == self.DEVICE_ID
        self.data = values[3]
        assert len(self.data) == self.data_length
        assert values[4] == byte_checksum(self._bytes[:-2])
        return self.data

    def serialize_bytes(self, little_endian=False):
        ''' Return hex representation of bytes '''
        return hexlify(self._pack_bytes(little_endian))

    def __bytes__(self):
        return self._pack_bytes(little_endian=True)


class FingerprintScanner(object):
    
    def __init__(self, debug=False, little_endian=False):
        self.debug = debug
        self.little_endian = little_endian
        try:
            self._serial = serial.Serial(port='/dev/ttyAMA0', baudrate=9600, timeout=None)
            self.open(timeout=0.1)
                
            self._serial.setBaudrate(115200)
            if self.open(): # baud rate 115200 succeeded
                self._serial.flush()
            else: # baud rate 115200 failed -> maybe still set to 9600?
                self._serial.setBaudrate(9600)
                if self.open(): # baud rate 9600 succeeded -> change to 115200
                        self.change_baudrate(115200)
                else: # baud rate 9600 failed; maybe already set to 115200?
                    raise serial.SerialException()

            # if self.open(): # baud rate 9600 succeeded -> change to 115200
            #     self.change_baudrate(115200)
            # else: # baud rate 9600 failed; maybe already set to 115200?
            #     self._serial.setBaudrate(115200)
            #     if self.open(): # baud rate 115200 succeeded
            #         self._serial.flush()
            #     else: # baud rate 115200 failed
            #         raise serial.SerialException()
        except serial.SerialException as e:
            raise Exception("Failed to connect to the fingerprint scanner!")

    def wait(self, seconds):
        time.sleep(seconds)

    def open(self, timeout=2):
        '''
            Initializes communication with the scanner
        '''
        self._send_command('Open')
        response = self._receive_response(timeout=timeout)
        if response is None:
            return False
        else:
            return response.ack

    def close(self):
        '''
            Ends communication with the scanner
            Does not actually do anything (according to the datasheet)
        '''
        response = self._run_command('Close')
        self._serial.close()
        return response.ack

    def set_backlight(self, on):
        '''
            Turns on or off the LED backlight
            LED must be on to see fingerprints
            Parameter: True turns on the backlight, False turns it off
        '''
        response = self._run_command('CmosLed', parameter = 1 if on else 0)
        return response.ack

    def backlight_on(self):
        return self.set_backlight(on=True)

    def backlight_off(self):
        return self.set_backlight(on=False)

    def change_baudrate(self, baudrate):
        '''
            Changes the baud rate of the connection
            Parameter: 9600 - 115200
            Returns: True if success, False if invalid baud
        '''
        if baudrate != self._serial.getBaudrate():
            if self._run_command('ChangeBaudrate', parameter=baudrate):
                if self.debug:
                    print('Changed baud rate from %s to %s' % (self._serial.getBaudrate(), baudrate))
                self._serial.setBaudrate(baudrate)
                return True
            else:
                return False
        else:
            return True

    def get_enroll_count(self):
        '''
            Returns: The total number of enrolled fingerprints
        '''
        response = self._run_command('GetEnrollCount')
        return response.parameter

    def is_enrolled(self, _id):
        '''
            Parameter: The ID to be checked
            Returns: True if the ID is enrolled, False if not
        '''
        response = self._run_command('CheckEnrolled', parameter=_id)
        return response.ack

    def find_free_id(self):
        '''
            Returns: The first free ID, -1 if db is full
        '''
        for _id in range(200):
            if not self.is_enrolled(_id):
                return _id
        return -1

    def enroll_finger(self, _id=None, blocking=True):
        '''
            The entire two-stage enrollment process
            Parameter: The ID to be enrolled (auto-searches for a free ID if not specified)
            Returns: The ID enrolled if successful, -1 if not
        '''
        if self.debug:
            print('Place your finger on the scanner')
        _id = self.start_enroll(_id)
        if _id >= 0:
            if self.debug:
                print('Enrolling with id %s' % _id)
                self.wait(1)
                print('Remove your finger from the scanner')
            # Wait for finger to be removed
            while self.is_finger_pressed():
                self.wait(1)
            if self.complete_enroll():
                return _id

        return -1

    def start_enroll(self, _id=None, blocking=True):
        '''
            First stage of enrollment process
            Parameter: The ID to be enrolled (auto-searches for a free ID if not specified)
            Returns: The ID to be enrolled if successful, -1 if not
        '''
        if _id: # user specified an ID
            if self.is_enrolled(_id): # ID is already enrolled
                if self.debug:
                    print('ID %s is already enrolled' % _id)
                return -1
        else:
            _id = self.find_free_id()
            if _id < 0: # database is full
                return -1

        if self._run_command('EnrollStart', parameter=_id): # Enroll start success
            if self._enroll(1, blocking):
                if self._enroll(2, blocking):
                    return _id
        return -1

    def complete_enroll(self, blocking=True):
        '''
            Last stage of enrollment process
            Returns: True if enrollment successfully finished, False if not
        '''
        return self._enroll(3, blocking)

    def _enroll(self, stage, blocking=True):
        '''
            Returns: True if enrollment successfully finished, False if not
        '''
        if self._capture_finger(blocking):
            response = self._run_command('Enroll' + str(stage))
            return response.ack
        return False

    def is_finger_pressed(self):
        '''
            Returns: True if there is a finger on the scanner, False if not
        '''
        response = self._run_command('IsPressFinger')
        return response.parameter == 0

    def delete_template(self, _id):
        '''
            Deletes the specified template ID from the database
            Returns: True if successful, False if position invalid
        '''
        response = self._run_command('DeleteID', parameter=_id)
        return response.ack

    def delete_all(self):
        '''
            Deletes all template IDs from the database
            Returns: True if successful, False if db is empty
        '''
        response = self._run_command('DeleteAll')
        return response.ack

    def verify_finger(self, _id, blocking=True):
        '''
            Checks the currently pressed finger against a specific ID
            Parameter: 0-199 (id number to be checked)
            Returns: True if match, False if not
        '''
        if self._capture_finger(high_quality=False, blocking=blocking):
            response = self._run_command('Verify1_1', parameter=_id)
            return response.ack
        else:
            return False
    
    def identify_finger(self, blocking=True):
        '''
            Checks the currently pressed finger against all enrolled fingerprints
            Returns:
                0-199: Matched with this ID
                -1   : Failed to find a match
        '''
        if self._capture_finger(high_quality=False, blocking=blocking):
            response = self._run_command('Identify1_N')
            return response.parameter if response.ack else -1
        else:
            return -1

    def verify_template(self, _id, template):
        if self._run_command('VerifyTemplate1_1', parameter=_id):
            self._send_data(data=template)
            response = self._receive_response()
            return response.ack
        return False

    def identify_template(self, template):
        if self._run_command('IdentifyTemplate1_N'):
            self._send_data(data=template)
            response = self._receive_response()
            if response.ack:
                return response.parameter
        return -1

    def _capture_finger(self, high_quality=True, blocking=True):
        '''
            Captures the currently pressed finger onto the onboard ram
            Parameters: Set high quality = True for enrollment, and False for verification/identification
                        If blocking = True, will loop forever until a finger is captured

            Returns: True if successful, False if no finger pressed
        '''
        self.backlight_on()
        while True:
            if self._run_command('CaptureFinger', parameter = 1 if high_quality else 0):
                self.backlight_off()
                return True
            elif not blocking: # give up
                self.backlight_off()
                return False
            else: # blocking -> try again
                self.wait(1.5)

    def make_template(self, blocking=True):
        if self._capture_finger(high_quality=True, blocking=blocking):
            if self._run_command('MakeTemplate'):
                data = self._receive_data(498)
                return data
        return None

    def make_image(self, blocking=True):
        if self._capture_finger(high_quality=True, blocking=blocking):
            if self._run_command('GetImage'):
                data = self._receive_data(52116)
                return data
        return None

    def make_raw_image(self):
        self.backlight_on()
        if self._run_command('GetRawImage'):
            data = self._receive_data(19200)
            self.backlight_off()
            return data
        self.backlight_off()
        return None

    def download_template(self, _id):
        '''
            Downloads a template from the database
            Parameter: 0-199 ID number
            Returns: the template requested (498 bytes)
        '''
        if self._run_command('GetTemplate', parameter=_id):
            data = self._receive_data(498)
            return data
        return None

    def upload_template(self, _id, template):
        '''
            Uploads a template to the database
            Parameter: 0-199 ID number, template (498 bytes)
            Returns: True if successful, False if not
        '''
        # the addition of 0x00ff0000 below is so that duplication check is not performed
        if self._run_command('SetTemplate', parameter=0x00ff0000 + _id):
            self._send_data(data=template)
            response = self._receive_response()
            return response.ack
        return False

    def _run_command(self, *args, **kwargs):
        self._send_command(*args, **kwargs)
        response = self._receive_response()
        return response

    def _send_command(self, *args, **kwargs):
        command = CommandPacket(*args, **kwargs)
        if self.debug:
            print('\nCommand:', command.name)
            print('sent:', command.serialize_bytes(little_endian=self.little_endian))
        self._serial.write(bytes(command))

    def _receive_response(self, timeout=None):
        self._serial.setTimeout(timeout)
        _bytes = self._serial.read(size=12)

        if len(_bytes) < 12:
            if self.debug:
                print('read:')
            return None
        
        response = ResponsePacket(_bytes)
        if self.debug:
            print('read:', response.serialize_bytes(little_endian=self.little_endian))
            if not response.ack:
                print('ERROR:', response.error)
        return response

    def _send_data(self, data):
        packet = DataPacket(data=data)
        if self.debug:
            print('data:', packet.serialize_bytes(little_endian=self.little_endian))
            print('dlen:', len(packet.data))
        self._serial.write(bytes(packet))

    def _receive_data(self, data_length, timeout=10):
        packet_length = data_length + 6 # the +6 comes from the other non-data parts of the packet

        self._serial.setTimeout(timeout)
        _bytes = self._serial.read(size=packet_length)
        assert self._serial.inWaiting() == 0 # that should be all

        if len(_bytes) < packet_length:
            return None

        packet = DataPacket(_bytes=_bytes)
        if self.debug:
            print('data:', packet.serialize_bytes(little_endian=self.little_endian))
            print('dlen:', len(packet.data))
        return packet.data


if __name__ == '__main__':
    fps = FingerprintScanner(debug=True)
    # fps.backlight_on()
    # for i in range(10):
    #     print(fps.is_finger_pressed())
    #     time.sleep(1)
    # fps.backlight_off()

    # Enrollment
    # enroll_id = fps.enroll_finger(blocking=True)

    # Identification
    # identify_id = fps.identify_finger(blocking=True)
    # if identify_id >= 0:
    #     print('Match with id %s' % identify_id)
    # else:
    #    print('No match found')

    # for i in range(5):
    #     template = fps.download_template(_id=i)

    fps.delete_all()
    template = fps.make_template(blocking=True)
    fps.upload_template(_id=0, template=template)
    # print fps.verify_template(_id=4, template=template)

    # print fps.verify_finger(_id=4, blocking=True)

    # fps.make_image()
    
    # from test_raw import SaveImage
    # SaveImage('fingerprint1.raw', fps.make_raw_image())
    # print(fps.make_raw_image())

    fps.close()
    print()