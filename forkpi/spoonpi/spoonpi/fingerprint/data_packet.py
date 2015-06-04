import struct
from .byte_utils import *

class DataPacket(object):
    """
    Packs / unpacks bytes that can be sent to / received from the FPS.

    Data packet format is:
        Byte     1       : START_CODE_1 (1 byte )
        Byte     2       : START_CODE_2 (1 byte )
        Byte     3-4     : DEVICE_ID    (2 bytes)
        Byte     5-{N+4} : data         (N bytes)
        Byte {N+5}-{N+6} : checksum     (2 bytes)

    Notes
    -----
        `START_CODE_1`, `START_CODE_2`, and `DEVICE_ID` are all fixed to the values specified below.

        The length of `data` is pre-defined depending on the protocol stage.

        `checksum` contains the sum of all other bytes, truncated to 2 bytes.

    Attributes
    ----------
    START_CODE_1 : int
        First byte of command packet. Fixed to 0x5A.
    START_CODE_2 : int
        Second byte of command packet. Fixed to 0xA5.
    DEVICE_ID : int
        Device ID. Fixed to 0x0001.
    bytes_ : bytes
        The data packet as sent by the FPS.
    data_length : int
        Length of the data (not the packet).
    data : bytes
        The data itself (without the other packet attributes).
    """

    START_CODE_1 = 0x5A
    START_CODE_2 = 0xA5
    DEVICE_ID = 0x0001

    def __init__(self, bytes_=None, data=None):
        """
        Parameters
        ----------
        bytes_ : bytes, optional
            The data packet as sent by the FPS, defaults to None.
            Set this variable when unpacking data from FPS.
        data : bytes
            The data portion of the packet, defaults to None.
            Set this variable when packing data to be sent to FPS.

        Raises
        ------
        AssertionError
            If both of, or neither of, bytes_ and data are set to None.
            When unpacking, if one of the start codes, device ID, or checksum is incorrect.

        """
        assert bytes_ or data # one of them
        assert not (bytes_ and data) # but not both
        if bytes_: # unpack data from bytes
            self.bytes_ = bytes_
            self.data_length = len(bytes_) - 6
            self._unpack_bytes()
        elif data: # pack data to bytes
            self.data = bytes(data)
            self.data_length = len(self.data)
            self._pack_bytes()

    def __bytes__(self):
        """
        Converts the data packet into bytes ready to be sent to the FPS.
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
        >>> bytes_ = bytes([0x5A, 0xA5, 0x01, 0x00, 0x01, 0x00, 0x01, 0x01])
        >>> data_packet = DataPacket(bytes_=bytes_)
        >>> data_packet.serialize_bytes()
        '5A A5 00 01 01 00 01 01'
        >>> data_packet.serialize_bytes(is_little_endian=True)
        '5A A5 01 00 01 00 01 01'

        """
        return hexlify(self._pack_bytes(is_little_endian))

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
            Bytes of the data packet formatted in the byte order specified.

        """
        if is_little_endian:
            byte_order = '<'
        else: # big endian
            byte_order = '>'

        bytes_ = struct.pack(byte_order + 'BBH%ds' % self.data_length, # byte byte word dword word
                self.START_CODE_1, self.START_CODE_2, self.DEVICE_ID, self.data)
        checksum = byte_checksum(bytes_)
        bytes_ += struct.pack(byte_order + 'H', checksum)
        self.bytes_ = bytes_
        return self.bytes_

    def _unpack_bytes(self):
        """
        Unpacks this object's attributes from the bytes according to the specified format.

        Raises
        ------
        AssertionError
            If one of the start codes, device ID, or checksum is incorrect.

        """
        values = struct.unpack('<BBH%dsH' % self.data_length, self.bytes_) # byte byte word var word
        assert values[0] == self.START_CODE_1
        assert values[1] == self.START_CODE_2
        assert values[2] == self.DEVICE_ID
        self.data = values[3]
        assert len(self.data) == self.data_length
        assert values[4] == byte_checksum(self.bytes_[:-2])
        return self.data