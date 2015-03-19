import struct
import serial
import binascii
import time

def hexlify(string):
    ''' Return hex representation of bytes '''
    return ' '.join(binascii.hexlify(ch) for ch in string)

def byte_checksum(string):
    ''' Sum of all bytes in string truncated to a byte '''
    return sum(map(ord, string)) & 0xFFFF


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

    def pack_bytes(self, little_endian=True):
        if little_endian:
            byte_order = '<'
        else: # big endian
            byte_order = '>'

        _bytes = struct.pack(byte_order + 'BBHIH', # byte byte word dword word
                self.START_CODE_1, self.START_CODE_2, self.DEVICE_ID, self.parameter, self.command_code)
        checksum = byte_checksum(_bytes)
        _bytes += struct.pack(byte_order + 'H', checksum)
        return _bytes

    def serialize_bytes(self, little_endian=False):
        _bytes = self.pack_bytes(little_endian)
        return hexlify(_bytes)
        

class ResponsePacket(object):

    START_CODE_1 = 0x55
    START_CODE_2 = 0xAA
    DEVICE_ID = 0x0001

    ERRORS = {
        0x0000: 'NO_ERROR'                  , # Default value. no error
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
        values = struct.unpack('<BBHIHH', self._bytes) # byte byte word dword word word
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
            self.error = self.ERRORS[self.error_code]

    def serialize_bytes(self, little_endian=False):
        ''' Return hex representation of bytes '''
        if little_endian:
            _bytes = self._bytes
        else:
            values = struct.unpack('<BBHIHH', self._bytes) # byte byte word dword word word
            _bytes = struct.pack('>BBHIHH', *values)
        return hexlify(_bytes)



class FingerprintScanner(object):

    DEVICE = '/dev/ttyAMA0'
    TIMEOUT = None
    
    def __init__(self, baudrate=9600, debug=False, little_endian=False):
        self.debug = debug
        self.little_endian = little_endian
        self._baudrate = baudrate
        try:
            self._serial = serial.Serial(port=self.DEVICE, baudrate=self._baudrate, timeout=self.TIMEOUT)
            self.open()
        except serial.SerialException, e:
            print "Failed to connect to the fingerprint scanner!"
            print str(e)

    def wait(self, seconds):
        time.sleep(seconds)

    def open(self):
        '''
            Initializes communication with the scanner
        '''
        self._send_command(CommandPacket('Open'))
        response = self._receive_response()
        return response.ack

    def close(self):
        '''
            Ends communication with the scanner
            Does not actually do anything (according to the datasheet)
        '''
        self._send_command(CommandPacket('Close'))
        response = self._receive_response()
        return response.ack

    def set_backlight(self, on):
        '''
            Turns on or off the LED backlight
            LED must be on to see fingerprints
            Parameter: True turns on the backlight, False turns it off
        '''
        self._send_command(CommandPacket('CmosLed', parameter = 1 if on else 0))
        response = self._receive_response()
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
            self._send_command(CommandPacket('ChangeBaudrate', parameter=baudrate))
            response = self._receive_response()
            if response.ack:
                if self.debug:
                    print 'Changed baud rate from %s to %s' % (self._baudrate, baudrate)
                self._serial.close()
                self.__init__(baudrate=baudrate, debug=self.debug, little_endian=self.little_endian)
            return response.ack
        else:
            return True

    def get_enroll_count(self):
        '''
            Returns: The total number of enrolled fingerprints
        '''
        self._send_command(CommandPacket('GetEnrollCount'))
        response = self._receive_response()
        return response.parameter

    def is_enrolled(self, _id):
        '''
            Parameter: The ID to be checked
            Returns: True if the ID is enrolled, False if not
        '''
        self._send_command(CommandPacket('CheckEnrolled', parameter=_id))
        response = self._receive_response()
        return response.ack

    def find_free_id(self):
        '''
            Returns: The first free ID, -1 if full
        '''
        for _id in range(200):
            if not self.is_enrolled(_id):
                return _id
        return -1

    def enroll_new(self, _id=None):
        '''
            Parameter: The ID to be enrolled (auto-searches for a free ID if not specified)
            Returns: The enrolled ID if successful, -1 if not
        '''
        if _id: # user specified an ID
            if self.is_enrolled(_id): # ID is already enrolled
                if self.debug:
                    print 'ID %s is already enrolled' % _id
                return -1
        else:
            _id = self.find_free_id()
            if _id < 0: # database is full
                return -1



        return _id


    def is_finger_pressed(self):
        '''
            Returns: True if there is a finger on the scanner, False if not
        '''
        self._send_command(CommandPacket('IsPressFinger'))
        response = self._receive_response()
        return response.parameter == 0
    
    def identify_finger(self):
        '''
            Checks the currently pressed finger against all enrolled fingerprints
            Returns:
                0-199: Matched with this ID
                -1   : Failed to find the fingerprint in the database
        '''
        self._capture_finger(high_quality=False)
        self._send_command(CommandPacket('Identify1_N'))
        response = self._receive_response()
        return response.parameter if response.ack else -1

    def _capture_finger(self, high_quality=True):
        '''
            Captures the currently pressed finger onto the onboard ram
            Parameter: True for high quality image (slower), False for low quality image (faster)
                       Use high quality for enrollment, and low quality for verification/identification
            Returns: True if successful, False if no finger pressed
        '''
        self._send_command(CommandPacket('CaptureFinger', parameter = 1 if high_quality else 0))
        response = self._receive_response()
        return response.ack

    def _send_command(self, command):
        if self.debug:
            print
            print 'Command:', command.name
            print 'sent:', command.serialize_bytes(little_endian=self.little_endian)
        self._serial.write(command.pack_bytes())

    def _receive_response(self):
        _bytes = self._serial.read(size=12)
        response = ResponsePacket(_bytes)
        if self.debug:
            print 'read:', response.serialize_bytes(little_endian=self.little_endian)
            if not response.ack:
                print 'ERROR:', response.error
        return response

    def _receive_data(self, length):
        self._serial.read()

if __name__ == '__main__':
    fps = FingerprintScanner(debug=False)
    fps.backlight_on()
    for i in range(5):
        if fps.is_finger_pressed():
            print 'Finger pressed!'
            _id = fps.identify_finger()
            if _id >= 0:
                print 'Match with id %s' % _id
            else:
                print 'No match found'
            break
        print 'No finger pressed'
        fps.wait(1)
    fps.backlight_off()
    fps.close()
    print