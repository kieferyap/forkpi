import struct
from .byte_utils import *

class ResponsePacket(object):
    """
    Unpacks bytes from the response packet sent by the FPS.

    Response packet format is:
        Byte  1    : START_CODE_1 (1 byte )
        Byte  2    : START_CODE_2 (1 byte )
        Byte  3-4  : DEVICE_ID    (2 bytes)
        Byte  5-8  : parameter    (4 bytes)
        Byte  9-10 : response     (2 bytes)
        Byte 11-12 : checksum     (2 bytes)

    Notes
    -----
        `START_CODE_1`, `START_CODE_2`, and `DEVICE_ID` are all fixed to the values specified below.

        `response` is 0x0030 if command is successful (ack).
                      0x0031 if command failed (nack).

        `parameter` contains the output parameter if ack.
                             the error code if nack.

        `checksum` contains the sum of all other bytes, truncated to 2 bytes.

    Attributes
    ----------
    START_CODE_1 : int
        First byte of command packet. Fixed to 0x55.
    START_CODE_2 : int
        Second byte of command packet. Fixed to 0xAA.
    DEVICE_ID : int
        Device ID. Fixed to 0x0001.
    ERRORS : dict
        Maps error codes to error names.
    bytes_ : bytes
        The response packet as sent by the FPS.
    ack : bool
        True if ack, False if nack.
    parameter : int
        Output parameter (if ack).
    error_code : int
        Error code (if nack).
    error : str
        Error description, mapped from `error_code` (if nack).

    """

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

    def __init__(self, bytes_):
        """
        Parameters
        ----------
        bytes_ : bytes
            The response packet as sent by the FPS.

        Raises
        ------
        AssertionError
            If one of the start codes, device ID, or checksum is incorrect.

        """
        self.bytes_ = bytes_
        self._unpack_bytes()

    def __bytes__(self):
        """
        Returns
        -------
        bytes
            The bytes passed upon initialization.

        """
        return self.bytes_

    def __bool__(self):
        """
        Allows the ResponsePacket object to function as a condition (e.g. in an if statement).

        Returns
        -------
        bool
            True if ack, False if nack

        """
        return self.ack

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
        >>> bytes_ = bytes([0x55, 0xAA, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0x00, 0x30, 0x01])
        >>> response = ResponsePacket(bytes_)
        >>> response.serialize_bytes() # big endian
        '55 AA 00 01 00 00 00 00 00 30 01 30'
        >>> response.serialize_bytes(is_little_endian=True)
        '55 AA 01 00 00 00 00 00 30 00 30 01'

        """
        if is_little_endian:
            bytes_ = self.bytes_
        else:
            values = struct.unpack('<BBHiHH', self.bytes_) # byte byte word dword word word
            bytes_ = struct.pack('>BBHiHH', *values)
        return hexlify(bytes_)

    def _unpack_bytes(self):
        """
        Unpacks this object's attributes from the bytes according to the specified format.

        Raises
        ------
        AssertionError
            If one of the start codes, device ID, or checksum is incorrect.

        """
        values = struct.unpack('<BBHiHH', self.bytes_) # byte byte word dword word word
        # assert values[0] == self.START_CODE_1
        # assert values[1] == self.START_CODE_2
        # assert values[2] == self.DEVICE_ID
        response = values[4]
        checksum = values[5]
        # assert checksum == byte_checksum(self.bytes_[:-2])
        self.ack = True if response == 0x30 else False
        if self.ack:
            self.parameter = values[3]
        else:
            self.error_code = values[3]
            self.error = self.ERRORS.get(self.error_code, "DUPLICATE_ID_" + str(self.error_code))