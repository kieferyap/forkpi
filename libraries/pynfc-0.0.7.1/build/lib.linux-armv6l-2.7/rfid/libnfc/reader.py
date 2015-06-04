'''Reader object modelled on Perl's libnfc binding by Xant'''
# Author: Boris Mazic
# Date: 29.05.2012
#package rfid.libnfc.reader

import sys, re, struct
from rfid.libnfc import pynfc, pycrypto1, py14443a
import rfid.libnfc.modulation.iso14443a.br106.factory
from rfid.libnfc.hexdump import hexdump, hexbytes


def modulation(modtype, baudrate):
    return '%02X|%02X' % (modtype, baudrate)

    
    
TAG_TYPES = {
    modulation(pynfc.NfcDevice.NMT_ISO14443A, pynfc.NfcDevice.NBR_106): rfid.libnfc.modulation.iso14443a.br106.factory.instantiate_tag
} 



def load_symbol(full_symbol_name):
    module_name, symbol_name = full_symbol_name.rsplit(".", 1)
    module = __import__(module_name)
    return getattr(module, symbol_name)

    
    
class Reader(object):
    ''' reader class allows to access RFID tags (actually only mifare ones have been implemented/tested) readable from any libnfc-compatible reader.'''
    
    
    def __init__(self, like=None, verbosity=1):
        dev_descs = pynfc.list_devices()
        if not dev_descs:
            raise RuntimeError('No readers found')
        
        if isinstance(like, int): 
            self.dev_desc = dev_descs[like]
        elif isinstance(like, str): 
            self.dev_desc = [d for d in dev_descs if re.search(d.device, like, flags=re.I|re.DOTALL)][0]
        else:
            self.dev_desc = dev_descs[0]
            
        # Connect to the reader and the tag
        self.reader = self.dev_desc.connect(target=False, verbosity=verbosity)


    def __repr__(self):
        s = [
            'Reader: %s' % self.name(),
            'Device Description:\n%s' % hexdump(buffer(self.dev_desc)),
            'Device:\n%s' % hexdump(buffer(self.reader._device.contents))
        ]
        return '\n'.join(s)


    def init(self):
        return self.reader.initiator_init()

    
    def name(self):
        '''returns the name of the current reader'''
        #len = pynfc.DEVICE_NAME_LENGTH
        #return struct.pack('%ds' % len, *self.dev_desc.device)
        #return self.dev_desc.device
        return self.reader._device.contents.acName


    def connect(self, modtype=pynfc.NfcDevice.NMT_ISO14443A, baudrate=pynfc.NfcDevice.NBR_106, blocking=False):
        '''
            Construct a tag object based on the provided tag type and the tag related data (read from the tag itself).
            Raise a runtime exception if no tag is found.
        '''
        # Deactivate the field
        self.reader.configure(pynfc.NfcDevice.NDO_ACTIVATE_FIELD, False)
        # Let the reader only try once to find a tag
        self.reader.configure(pynfc.NfcDevice.NDO_INFINITE_SELECT, blocking)
        self.reader.configure(pynfc.NfcDevice.NDO_HANDLE_CRC, True)
        self.reader.configure(pynfc.NfcDevice.NDO_HANDLE_PARITY, True)
        # Enable field so more power consuming cards can power themselves up
        self.reader.configure(pynfc.NfcDevice.NDO_ACTIVATE_FIELD, True)
        
        uid = None    # see libnfc/nfc.c/nfc_initiator_select_passive_target()
        target = self.reader.select_passive_target(modtype, baudrate, uid)
        if not target:
            raise RuntimeError('No tag was found')
        
        instantiate_tag = TAG_TYPES[modulation(modtype, baudrate)]
        return instantiate_tag(self.reader, target)



        

