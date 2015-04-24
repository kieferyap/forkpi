import binascii

def hexlify(bytes_):
    """
    Parameters
    ----------
    bytes_ : bytes

    Returns
    -------
    str
        Hex representation of bytes_ separated by spaces

    Example
    -------
    >>> hexlify(bytes([0xA1, 0x2F, 0xC3]))
    'A1 2F C3'

    """
    # return ' '.join(binascii.hexlify(ch) for ch in bytes_)
    # return binascii.hexlify(bytes_)
    return ' '.join(["{0:0>2X}".format(b) for b in bytes_])

def byte_checksum(bytes_):
    """
    Parameters
    ----------
    bytes_ : bytes

    Returns
    -------
    int
        Sum of all bytes in bytes_ truncated to a word (two bytes)

    Example
    -------
    >>> byte_checksum(bytes([0xF0, 0x0F]))
    255

    """
    return sum(bytes_) & 0xFFFF