'''
Created on 15 Jan 2011

@author: mike
'''

import sys, struct
import ctypes
import ctypes.util
from rfid.libnfc.hexdump import hexdump, hexbytes


libnfc = 'libnfc' if sys.platform.startswith("win") else 'nfc'
_lib = ctypes.CDLL(ctypes.util.find_library(libnfc))

DEVICE_NAME_LENGTH = 256
MAX_FRAME_LEN = 264
DEVICE_PORT_LENGTH = 64


(NC_PN531, NC_PN532, NC_PN533) = (0x10, 0x20, 0x30)

_byte_t = ctypes.c_ubyte
_size_t = ctypes.c_size_t
_enum_val = ctypes.c_int

# libnfc-1.5.1/include/nfc/nfc-types.h:80
class DeviceDescription(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("device", ctypes.c_char * DEVICE_NAME_LENGTH),
                ("driver", ctypes.c_char_p),
                ("port", ctypes.c_char * DEVICE_PORT_LENGTH),
                ("speed", ctypes.c_uint32),
                ("bus_index", ctypes.c_uint32)
                ]

    def connect(self, target=None, verbosity=0):
        if target == False:
            return NfcInitiator(self, verbosity=verbosity)
        if target == True:
            return NfcTarget(self, verbosity=verbosity)
        return NfcDevice(self, verbosity=verbosity)

class ChipCallbacks(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("strerror", ctypes.POINTER(None))
                ]

class InfoIso14443A(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("atqa", _byte_t * 2),
                ("sak", _byte_t),
                ("uidlen", _size_t),
                ("uid", _byte_t * 10),
                ("atslen", _size_t),
                ("ats", _byte_t * 254) # Maximal theoretical ATS is FSD - 2, FSD = 256 for FSDI = 8 in RATS
                ]

class InfoFelicia(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("len", _size_t),
                ("res_code", _byte_t),
                ("id", _byte_t * 8),
                ("pad", _byte_t * 8),
                ("sys_code", _byte_t * 2)
                ]

class InfoIso14443B(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("pupi", _byte_t * 4),
                ("application_data", _byte_t * 4),
                ("protocol_info", _byte_t * 3),
                ("card_identifier", ctypes.c_uint8)
                ]

class InfoJewel(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("sens_res", _byte_t * 2),
                ("id", _byte_t * 4)
                ]

class InfoDep(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("nfcid3", _byte_t * 10),
                ("did", _byte_t),
                ("bs", _byte_t),
                ("br", _byte_t),
                ("to", _byte_t),
                ("pp", _byte_t),
                ("gb", _byte_t * 48),
                ("gb_size", _size_t),
                ("ndm", _enum_val)
                ]

class TargetInfo(ctypes.Union):
    _pack_ = 1
    _fields_ = [("nai", InfoIso14443A),
                ("nfi", InfoFelicia),
                ("nbi", InfoIso14443B),
                ("nji", InfoJewel),
                ("ndi", InfoDep)
                ]

class Modulation(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("nmt", _enum_val),
                ("nbr", _enum_val)
                ]

class Target(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("nti", TargetInfo),
                ("mm", Modulation)
                ]

class DriverCallbacks(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("driver", ctypes.c_char_p),
                ("chip_callbacks", ctypes.POINTER(ChipCallbacks)),
                ("pick_device", ctypes.POINTER(None)),
                ("list_devices", ctypes.POINTER(None)),
                ("connect", ctypes.POINTER(None)),
                ("transceive", ctypes.POINTER(None)),
                ("disconnect", ctypes.POINTER(None))
                ]

# libnfc-1.5.1/include/nfc/nfc-types.h:44
class _Device(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('driver', ctypes.POINTER(None)),
        ('driver_data', ctypes.POINTER(None)),
        ('chip_data', ctypes.POINTER(None)),
        ('acName', ctypes.c_char * DEVICE_NAME_LENGTH),
        ("bCrc", ctypes.c_bool),
        ("bPar", ctypes.c_bool),
        ("bEasyFraming", ctypes.c_bool),
        ("bAutoIso14443_4", ctypes.c_bool),
        ("btSupportByte", ctypes.c_ubyte),
        ("iLastError", ctypes.c_int)
    ]

                
                
_lib.nfc_version.restype = ctypes.c_char_p

_lib.nfc_list_devices.argtypes = (ctypes.POINTER(DeviceDescription),
                                _size_t,
                                ctypes.POINTER(_size_t))

_lib.nfc_connect.argtypes = (ctypes.POINTER(DeviceDescription),)
_lib.nfc_connect.restype = ctypes.POINTER(_Device)

_lib.nfc_disconnect.argtypes = (ctypes.POINTER(DeviceDescription),)
_lib.nfc_disconnect.restype = None

_lib.nfc_configure.argtypes = (ctypes.POINTER(_Device),
                            _enum_val,
                            ctypes.c_bool)
_lib.nfc_configure.restype = ctypes.c_bool

_lib.nfc_initiator_init.argtypes = (ctypes.POINTER(_Device),)
_lib.nfc_initiator_init.restype = ctypes.c_bool

_lib.nfc_initiator_select_passive_target.argtypes = (ctypes.POINTER(_Device),
                                                    Modulation,
                                                    ctypes.POINTER(_byte_t),
                                                    _size_t,
                                                    ctypes.POINTER(Target))
_lib.nfc_initiator_select_passive_target.restype = ctypes.c_bool

_lib.nfc_initiator_list_passive_targets.argtypes = (ctypes.POINTER(_Device),
                                                    Modulation,
                                                    ctypes.POINTER(Target),
                                                    _size_t,
                                                    ctypes.POINTER(_size_t))
_lib.nfc_initiator_list_passive_targets.restype = ctypes.c_bool

_lib.nfc_initiator_select_dep_target.argtypes = (ctypes.POINTER(_Device),
                                                _enum_val,
                                                _enum_val,
                                                ctypes.POINTER(InfoDep),
                                                ctypes.POINTER(Target))
_lib.nfc_initiator_select_passive_target.restype = ctypes.c_bool

_lib.nfc_initiator_deselect_target.argtypes = (ctypes.POINTER(_Device),)
_lib.nfc_initiator_deselect_target.restype = ctypes.c_bool

_lib.nfc_initiator_transceive_bytes.argtypes = (ctypes.POINTER(_Device),
                                                ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                                _size_t,
                                                ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                                ctypes.POINTER(_size_t))
_lib.nfc_initiator_transceive_bytes.restype = ctypes.c_bool

_lib.nfc_initiator_transceive_bits.argtypes = (ctypes.POINTER(_Device),
                                            ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                            _size_t,
                                            ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                            ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                            ctypes.POINTER(_size_t),
                                            ctypes.POINTER(_byte_t * MAX_FRAME_LEN))
_lib.nfc_initiator_transceive_bits.restype = ctypes.c_bool

_lib.nfc_strerror.argtypes = (ctypes.POINTER(_Device),)
_lib.nfc_strerror.restype = ctypes.c_char_p

_lib.nfc_target_init.argtypes = (ctypes.POINTER(_Device),
                                ctypes.POINTER(Target),
                                ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                ctypes.POINTER(_size_t))
_lib.nfc_target_init.restype = ctypes.c_bool

_lib.nfc_target_receive_bits.argtypes = (ctypes.POINTER(_Device),
                                        ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                        ctypes.POINTER(_size_t),
                                        ctypes.POINTER(_byte_t * MAX_FRAME_LEN))
_lib.nfc_target_receive_bits.restype = ctypes.c_bool

_lib.nfc_target_receive_bytes.argtypes = (ctypes.POINTER(_Device),
                                        ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                        ctypes.POINTER(_size_t))
_lib.nfc_target_receive_bytes.restype = ctypes.c_bool

_lib.nfc_target_send_bits.argtypes = (ctypes.POINTER(_Device),
                                    ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                    _size_t,
                                    ctypes.POINTER(_byte_t * MAX_FRAME_LEN))
_lib.nfc_target_send_bits.restype = ctypes.c_bool

_lib.nfc_target_send_bytes.argtypes = (ctypes.POINTER(_Device),
                                    ctypes.POINTER(_byte_t * MAX_FRAME_LEN),
                                    _size_t)
_lib.nfc_target_send_bytes.restype = ctypes.c_bool

def get_version():
    res = _lib.nfc_version()
    print res

def list_devices():
    max_device_length = 16
    Devices = DeviceDescription * max_device_length
    pnddDevices = Devices()
    num_devices = _size_t(0)
    _lib.nfc_list_devices(pnddDevices, max_device_length, ctypes.byref(num_devices))
    result = []
    for i in range(min(num_devices.value, max_device_length)):
        result.append(pnddDevices[i])
    return result

class NfcDevice(object):
    NDO_HANDLE_CRC = 0x00
    NDO_HANDLE_PARITY = 0x01
    NDO_ACTIVATE_FIELD = 0x10
    NDO_ACTIVATE_CRYPTO1 = 0x11
    NDO_INFINITE_SELECT = 0x20
    NDO_ACCEPT_INVALID_FRAMES = 0x30
    NDO_ACCEPT_MULTIPLE_FRAMES = 0x31
    NDO_AUTO_ISO14443_4 = 0x40
    NDO_EASY_FRAMING = 0x41
    NDO_FORCE_ISO14443_A = 0x42

    NMT_ISO14443A = 0x0
    NMT_ISO14443B = 0x1
    NMT_FELICA = 0x2
    NMT_JEWEL = 0x3
    NMT_DEP = 0x4

    NBR_UNDEFINED = 0x0
    NBR_106 = 0x01
    NBR_212 = 0x02
    NBR_424 = 0x03
    NBR_847 = 0x04

    NDM_UNDEFINED = 0x0
    NDM_PASSIVE = 0x01
    NDM_ACTIVE = 0x02

    def __init__(self, devdesc = None, verbosity=0):
        self._device = _lib.nfc_connect(ctypes.byref(devdesc))

        # Create the buffers so that we don't have to inefficiently recreate them each call
        self._txbytes = (_byte_t * MAX_FRAME_LEN)()
        self._txpbytes = (_byte_t * MAX_FRAME_LEN)()
        self._rxbytes = (_byte_t * MAX_FRAME_LEN)()
        self._rxpbytes = (_byte_t * MAX_FRAME_LEN)()
        self.verbosity = verbosity

    def _check_enum(self, prefix, value):
        if value not in [ getattr(self, i) for i in dir(self) if i.startswith(prefix)]:
            raise AttributeError("Failed to locate appropriate configuration option")

    def configure(self, option, value):
        """Configures the NFC device options"""
        self._check_enum('NDO', option)
        return _lib.nfc_configure(self._device, option, value)

    def initiator_init(self):
        """Initializes the NFC device for initiator"""
        return _lib.nfc_initiator_init(self._device)

    def initiator_select_passive_target(self, modtype, baudrate, initdata = None):
        """Selects a passive target"""
        self._check_enum('NMT', modtype)
        self._check_enum('NBR', baudrate)

        mod = Modulation(nmt = modtype, nbr = baudrate)

        if not initdata:
            data = None
            data_len = 0
        else:
            Data = ctypes.c_ubyte * len(initdata)
            data = ctypes.byref(Data(initdata))
            data_len = len(initdata)

        target = Target()
        _lib.nfc_initiator_select_passive_target(self._device,
                                                mod,
                                                data,
                                                data_len,
                                                ctypes.byref(target))
        return target

    def initiator_list_passive_targets(self, modtype, baudrate):
        """Lists all available passive targets"""
        self._check_enum('NMT', modtype)
        self._check_enum('NBR', baudrate)

        mod = Modulation(nmt = modtype, nbr = baudrate)

        max_targets_length = 16
        Targets = Target * max_targets_length
        targets = Targets()
        num_targets = _size_t(0)

        _lib.nfc_initiator_list_passive_targets(self._device,
                                                mod,
                                                targets,
                                                max_targets_length,
                                                ctypes.byref(num_targets))

        result = []
        for i in range(min(num_targets.value, max_targets_length)):
            result.append(targets[i])
        return result

    def initiator_deselect_target(self):
        """Deselects any selected target"""
        return _lib.nfc_initiator_deselect_target(self._device)

    def initiator_select_dep_target(self, depmode, baudrate, depinfo):
        """Selects a dep target"""
        self._check_enum('NDM', depmode)
        self._check_enum('NBR', baudrate)

        if not depinfo:
            data = None
        else:
            data = ctypes.byref(depinfo)

        target = Target()
        _lib.nfc_initiator_select_dep_target(self._device,
                                            depmode,
                                            baudrate,
                                            data,
                                            ctypes.byref(target))
        return target

    def initiator_poll_targets(self, targetlist, pollnum, period):

        targtypes = Modulation * len(targetlist)
        for i in range(len(targetlist)):
            targtypes[i] = targetlist[i]

        max_targets_length = 16
        Targets = Target * max_targets_length
        targets = Targets()
        num_targets = _size_t(0)
        _lib.nfc_initiator_poll_targets(self._device, ctypes.byref(targtypes),
                                        _size_t(len(targetlist)),
                                        _byte_t(pollnum),
                                        _byte_t(period),
                                        ctypes.byref(targets),
                                        ctypes.byref(num_targets))
        result = []
        for i in range(min(num_targets.value, max_targets_length)):
            result.append(targets[i])
        return result

    def initiator_transceive_bits(self, bits, numbits, paritybits = None):
        """Sends a series of bits, returning the number and bits sent back by the target"""
        if paritybits and len(paritybits) != len(bits):
            raise ValueError("Length of parity bits does not match length of bits")
        if len(bits) < ((numbits + 7) / 8):
            raise ValueError("Length of bits does not match the value passed in numbits")

        insize = min(((numbits + 7) / 8), MAX_FRAME_LEN)
        for i in range(insize):
            self._txbytes[i] = ord(bits[i])
            if paritybits:
                self._txpbytes[i] = ord(paritybits[i]) & 0x01

        parity = None
        if paritybits:
            parity = ctypes.pointer(self._txpbytes)

        rxbitlen = _size_t(0)

        result = _lib.nfc_initiator_transceive_bits(self._device,
                                                    ctypes.pointer(self._txbytes),
                                                    _size_t(numbits),
                                                    parity,
                                                    ctypes.pointer(self._rxbytes),
                                                    ctypes.byref(rxbitlen),
                                                    ctypes.pointer(self._rxpbytes))
        if not result:
            return None

        rxbytes = rxpbytes = ""
        for i in range(min(((rxbitlen.value + 7) / 8), MAX_FRAME_LEN)):
            rxbytes += chr(self._rxbytes[i])
            rxpbytes += chr(self._rxpbytes[i])

        return rxbytes, rxbitlen.value, rxpbytes


    def initiator_transceive_bytes(self, inbytes):
        """Sends a series of bytes, returning those bytes sent back by the target"""
        if self.verbosity > 0: print 'R>T[%2X]: %s' % (len(inbytes), hexbytes(inbytes))
        insize = min(len(inbytes), MAX_FRAME_LEN)
        for i in range(insize):
            self._txbytes[i] = ord(inbytes[i])

        rxbytelen = _size_t(0)

        result = _lib.nfc_initiator_transceive_bytes(self._device,
                                                    ctypes.byref(self._txbytes),
                                                    _size_t(insize),
                                                    ctypes.byref(self._rxbytes),
                                                    ctypes.byref(rxbytelen))

        if not result:
            if self.verbosity > 0: print 'T%2X[--]:' % (result)
            return None

        if self.verbosity > 0: print 'T%2X[%2X]: %s' % (result, rxbytelen.value, hexbytes(buffer(self._rxbytes)[:rxbytelen.value]))

        result = ""
        for i in range(min(rxbytelen.value, MAX_FRAME_LEN)):
            result += chr(self._rxbytes[i])

        return result


        
    def get_error(self):
        """Returns an error description for any error that may have occurred from the previous command"""
        return _lib.nfc_strerror(self._device)

    def target_init(self, targettype = None):
        """Initializes the device as a target"""
        rxsize = _size_t(0)

        if targettype:
            targettype = ctypes.byref(targettype)

        return _lib.nfc_target_init(self._device,
                                    targettype,
                                    self._rxbytes,
                                    ctypes.byref(rxsize))

    def target_receive_bits(self):
        """Receives bits and parity bits from a device in target mode"""
        rxsize = _size_t(0)
        result = _lib.nfc_target_receive_bits(self._device,
                                            ctypes.byref(self._rxbytes),
                                            ctypes.byref(rxsize),
                                            ctypes.byref(self._rxpbytes))

        if not result:
            return None

        rxbytes = rxpbytes = ""
        for i in range(min(((rxsize.value + 7) / 8), MAX_FRAME_LEN)):
            rxbytes += chr(self._rxbytes[i])
            rxpbytes += chr(self._rxpbytes[i])

        return rxbytes, rxsize.value, rxpbytes

    def target_receive_bytes(self):
        """Receives bytes from a device in target mode"""
        rxsize = _size_t(0)
        result = _lib.nfc_target_receive_bytes(self._device,
                                            ctypes.byref(self._rxbytes),
                                            ctypes.byref(rxsize))

        if not result:
            return None

        result = ""
        for i in range(rxsize.value):
            result += chr(self._rxbytes[i])
        return result

    def target_send_bits(self, bits, numbits, paritybits = None):
        """Sends bits and paritybits in target mode"""
        if paritybits and len(paritybits) != len(bits):
            raise ValueError("Length of parity bits does not match length of bits")
        if len(bits) < ((numbits + 7) / 8):
            raise ValueError("Length of bits does not match the value passed in numbits")

        insize = min(((numbits + 7) / 8), MAX_FRAME_LEN)
        for i in range(insize):
            self._txbytes[i] = ord(bits[i])
            if paritybits:
                self._txpbytes[i] = ord(paritybits[i]) & 0x01

        parity = None
        if paritybits:
            parity = ctypes.byref(self._txpbytes)

        return _lib.nfc_target_send_bits(self._device,
                                        ctypes.byref(self._txbytes),
                                        _size_t(numbits),
                                        parity)

    def target_send_bytes(self, inbytes):
        """Sends bytes in target mode"""
        insize = min(len(inbytes), MAX_FRAME_LEN)
        for i in range(insize):
            self._txbytes[i] = ord(inbytes[i])

        return _lib.nfc_target_send_bytes(self._device,
                                        ctypes.byref(self._txbytes),
                                        _size_t(insize))



class NfcTarget(NfcDevice):

    def __init__(self, devdesc, targettype = None, *args, **kwargs):
        NfcDevice.__init__(self, devdesc, *args, **kwargs)
        self.init(targettype)

    def init(self, *args, **kwargs):
        return self.target_init(*args, **kwargs)

    def receive_bits(self, *args, **kwargs):
        return self.target_receive_bits(*args, **kwargs)

    def receive_bytes(self, *args, **kwargs):
        return self.target_receive_bytes(*args, **kwargs)

    def send_bits(self, *args, **kwargs):
        return self.target_send_bits(*args, **kwargs)

    def send_bytes(self, *args, **kwargs):
        return self.target_send_bytes(*args, **kwargs)

class NfcInitiator(NfcDevice):

    def __init__(self, *args, **kwargs):
        NfcDevice.__init__(self, *args, **kwargs)
        self.init()

    def init(self, *args, **kwargs):
        return self.initiator_init(*args, **kwargs)

    def select_passive_target(self, *args, **kwargs):
        return self.initiator_select_passive_target(*args, **kwargs)

    def list_passive_targets(self, *args, **kwargs):
        return self.initiator_list_passive_targets(*args, **kwargs)

    def deselect_target(self, *args, **kwargs):
        return self.initiator_deselect_target(*args, **kwargs)

    def select_dep_target(self, *args, **kwargs):
        return self.initiator_select_dep_target(*args, **kwargs)

    def poll_targets(self, *args, **kwargs):
        return self.initiator_poll_targets(*args, **kwargs)

    def transceive_bits(self, *args, **kwargs):
        return self.initiator_transceive_bits(*args, **kwargs)

    def transceive_bytes(self, *args, **kwargs):
        return self.initiator_transceive_bytes(*args, **kwargs)

if __name__ == '__main__':
    devs = list_devices()
    dev = devs[0].connect()
    dev.initiator_init()
    # dev.initiator_select_passive_target(dev.NMT_ISO14443A, dev.NBR_UNDEFINED, "")
