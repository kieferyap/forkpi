'''
Base class for the ISO14443A_106 compliant tags.
You will never use this module directly but all the logic 
common to all ISO14443A_106 tags should be placed here 
(and inherited by all specific tag-implementations)
'''
# Author: Boris Mazic
# Date: 29.05.2012
#package rfid.libnfc.modulation.iso14443a.br106.tag

import struct
from rfid.libnfc import tag
from rfid.libnfc.hexdump import hexdump, hexbytes, hexprint



TAG_TYPE = {
    0x00: "MIFARE Ultra"
    , 0x08: "MIFARE Classic_1K"
    , 0x09: "MIFARE Classic_MINI"
    , 0x18: "MIFARE Classic_4K"
    , 0x20: "MIFARE DESFire"
    , 0x28: "JCOP30"
    , 0x38: "JCOP40"
    , 0x88: "Oyster"
    , 0x98: "Gemplus_MPCOS"
}



class Tag(tag.Tag):
    def __init__(self, reader, target):
        self.reader = reader
        self.target = target
    
    def __repr__(self):
        s = '%s: %s\n' % ('Type', self.type())
        return  s + '\n'.join('%s: %s' % (k, hexbytes(v)) 
            for k,v in {
                'UID': self.uid(),
                'ATAQ': self.atqa(),
                'SAK': self.sak(),
                'ATS': self.ats()
            }.iteritems())

    def atqa(self):
        return struct.pack('2B', *self.target.nti.nai.atqa)

    def sak(self):
        return struct.pack('B', self.target.nti.nai.sak)

    def uid(self):
        len = self.target.nti.nai.uidlen
        return struct.pack('%dB' % len, *self.target.nti.nai.uid[:len])

    def ats(self):
        len = self.target.nti.nai.atslen
        return struct.pack('%dB' % len, *self.target.nti.nai.ats[:len])

    def type(self):
        '''returns the specific tag type actually hooked'''
        return TAG_TYPE.get(self.target.nti.nai.sak, '<unknown>')



