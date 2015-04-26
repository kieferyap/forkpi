import struct
from .byte_utils import *

class CommandPacket(object):
    """
    Packs commands and parameters into bytes that can be sent.

    Command packet format is:
        Byte  1    : START_CODE_1  (1 byte )
        Byte  2    : START_CODE_2  (1 byte )
        Byte  3-4  : DEVICE_ID     (2 bytes)
        Byte  5-8  : parameter     (4 bytes)
        Byte  9-10 : command code  (2 bytes)
        Byte 11-12 : checksum      (2 bytes)

    Notes
    -----
        `START_CODE_1`, `START_CODE_2`, and `DEVICE_ID` are all fixed to the values specified below.

        `checksum` contains the sum of all other bytes, truncated to 2 bytes.

    Attributes
    ----------
    START_CODE_1 : int
        First byte of command packet. Fixed to 0x55.
    START_CODE_2 : int
        Second byte of command packet. Fixed to 0xAA.
    DEVICE_ID : int
        Device ID. Fixed to 0x0001.
    COMMANDS : dict
        Maps command names to command codes.
    name : str
        Command name, must be in COMMANDS.
    command_code : str
        Command code, mapped from `name`.
    parameter : int
        Command parameter.

    """

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
        """
        Parameters
        ----------
        command_name : str
            Command name, name must be in COMMANDS.
        parameter : int, optional
            Command parameter , defaults to 0.

        Raises
        ------
        ValueError
            If `command_name` is not in `COMMANDS`.

        """
        if command_name in self.COMMANDS:
            self.name = command_name
            self.command_code = self.COMMANDS[command_name]
            self.parameter = parameter
        else:
            raise ValueError("%s not in command list" % command_name)

    def __bytes__(self):
        """
        Converts the command packet into bytes ready to be sent to the FPS.
        Bytes are formatted in little endian order.

        Returns
        ------
        bytes
            Packed bytes in little endian order.

        """
        return self._pack_bytes(is_little_endian=True)
  
    def serialize_bytes(self, is_little_endian=False):
        """
        Parameters
        ----------
        is_little_endian : bool, optional
            Byte order, defaults to False.
            True for little endian, False for big endian.

        Returns
        ------
        str
            Hex representation of packed bytes in the byte order specified.

        Example
        -------
        >>> command = CommandPacket('Open', parameter=1)
        >>> command.serialize_bytes() # big endian
        '55 AA 00 01 00 00 00 01 00 01 01 02'
        >>> command.serialize_bytes(is_little_endian=True)
        '55 AA 01 00 01 00 00 00 01 00 02 01'

        """
        bytes_ = self._pack_bytes(is_little_endian)
        return hexlify(bytes_)
    
    def _pack_bytes(self, is_little_endian=True):
        """
        Packs this object's attributes into bytes according to the specified format.

        Parameters
        ----------
        is_little_endian : bool, optional
            Byte order, defaults to True.
            True for little endian, False for big endian.

        Returns
        -------
        bytes
            Bytes of the command packet formatted in the byte order specified.

        """
        if is_little_endian:
            byte_order = '<'
        else: # big endian
            byte_order = '>'

        bytes_ = struct.pack(byte_order + 'BBHiH', # byte byte word dword/(signed int) word
                self.START_CODE_1, self.START_CODE_2, self.DEVICE_ID, self.parameter, self.command_code)
        checksum = byte_checksum(bytes_)
        bytes_ += struct.pack(byte_order + 'H', checksum)
        return bytes_
