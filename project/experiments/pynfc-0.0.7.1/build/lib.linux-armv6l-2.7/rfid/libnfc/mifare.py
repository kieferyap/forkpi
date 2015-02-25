'''MIFARE Classic Command Support (A Monkey Patch to pynfc module)'''
# Author: Boris Mazic
# Date: 04.06.2012
#package rfid.libnfc.mifare

import struct
import ctypes
from rfid.libnfc import pynfc
from rfid.libnfc.hexdump import hexbytes


# MIFARE commands
MC_AUTH_A         = 0x60
MC_AUTH_B         = 0x61
MC_READ         = 0x30
MC_WRITE         = 0xA0
MC_TRANSFER     = 0xB0
MC_DECREMENT     = 0xC0
MC_INCREMENT     = 0xC1
MC_STORE         = 0xC2

MU_REQA     = 0x26
MU_WUPA     = 0x52
MU_SELECT1     = 0x93
MU_SELECT2     = 0x95
MU_READ     = 0x30
MU_WRITE     = 0xA2
MU_CWRITE     = 0xA0
MU_HALT     = 0x50



# MIFARE command params
#------------------------------------------------------------------------------
# libnfc-1.5.1/utils/mifare.h:55
class mifare_param_auth(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("abtKey", ctypes.c_ubyte*6),
        ("abtUid", ctypes.c_ubyte*4)
    ]
    
    def __repr__(self):
        return 'mifare_param_auth(abtKey=%s, abtUid=%s)' % (hexbytes(self.abtKey), hexbytes(self.abtUid))
        
    def __init__(self, key, uid):
        self.set_key(key)
        self.set_uid(uid)

    def set_key(self, key):
        if isinstance(key, str):
            self.abtKey = struct.unpack('6B', key)
        else:
            k = struct.pack('>Q', key)
            self.abtKey = struct.unpack('2x6B', k)

    def set_uid(self, uid):
        if isinstance(uid, str):
            self.abtUid = struct.unpack('4B', uid)
        else:
            u = struct.pack('>L', uid)
            self.abtUid = struct.unpack('4B', u)
        
    def _test(self):
        p = mifare_param_auth()
        p.set_key(0xa0a1a2a3a4a5)
        p.set_uid(0x89ABCDEF)
        print p
        p.set_key(struct.pack('6B', *p.abtKey))
        p.set_uid(struct.pack('4B', *p.abtUid))
        print p




class mifare_param_data(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("abtData", ctypes.c_ubyte*16)
    ]

    def __init__(self, data):
        self.set_data(data)

    def set_data(self, data):
        self.abtData = struct.unpack('16B', data)
        
    def get_data(self):
        return struct.pack('16B', *self.abtData)



class mifare_param_value(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("abtValue", ctypes.c_ubyte*4)
    ]

    def set_value(self, value):
        self.abtValue = struct.unpack('4B', value)



class mifare_param(ctypes.Union):
    _pack_ = 1
    _fields_ = [
        ("mpa", mifare_param_auth),
        ("mpd", mifare_param_data),
        ("mpv", mifare_param_value)
    ]

    

class mifare_cmd(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("cmd", ctypes.c_ubyte),
        ("block", ctypes.c_ubyte),
        ('param', mifare_param)
    ]
    
    def __init__(self, cmd, block):
        self.cmd = cmd
        self.block = block



def send_cmd(reader, cmd_block):
    '''Send MIFARE command + parameters'''
    easy_framing = reader._device.contents.bEasyFraming
    reader.configure(pynfc.NfcDevice.NDO_EASY_FRAMING, True)
    r = reader.transceive_bytes(cmd_block)
    reader.configure(pynfc.NfcDevice.NDO_EASY_FRAMING, easy_framing)
    return r



def read(reader, block):
    '''Send MC_READ=0x30 command'''
    cmd = mifare_cmd(MC_READ, block)
    data = send_cmd(reader, buffer(cmd)[:2])
    if data is None:
        raise RuntimeError('MIFARE: Reading block %d failed' % block)
    return data



def write(reader, block, data):
    '''Send MC_WRITE=0xA0 command'''
    cmd = mifare_cmd(MC_WRITE, block)
    cmd.param.mpd = mifare_param_data(data)
    data_size = len(data)
    return send_cmd(reader, buffer(cmd)[:2+data_size]) is not None



def auth(reader, block, keytype, key, uid):
    '''Send MC_AUTH_A or MC_AUTH_B command'''
    cmd = mifare_cmd(keytype, block)
    cmd.param.mpa = mifare_param_auth(key, uid)
    data_size = ctypes.sizeof(cmd.param.mpa)
    return send_cmd(reader, buffer(cmd)[:2+data_size]) is not None

