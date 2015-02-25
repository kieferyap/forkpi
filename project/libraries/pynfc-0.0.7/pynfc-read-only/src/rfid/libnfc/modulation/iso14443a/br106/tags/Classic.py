'''MIFARE Classic tag base class (modelled on Perl's libnfc binding by Xant)'''
# Author: Boris Mazic
# Date: 29.05.2012
#package rfid.libnfc.modulation.iso14443a.br106.tags.Classic

import struct
from rfid.libnfc import pynfc, mifare
import rfid.libnfc.modulation.iso14443a.br106.tag
from rfid.libnfc.modulation.iso14443a.br106.tags import Classic_Keys



# used for indexing into trailer_acl and data_acl (see auth() function)
READ, WRITE = (0,1)


# Internal representation of TABLE 3 (M001053_MF1ICS50_rev5_3.pdf)
# the key are the actual ACL bits (C1 C2 C3) ,
# the value holds read/write condition for : KeyA, ACL, KeyB
# possible values for read and write conditions are :
#    0 - operation not possible
#    1 - operation possible using Key A
#    2 - operation possible using Key B
#    3 - operation possible using either Key A or Key B
#   
# for instance: 
#
#   3 => { A => [ 0, 2 ], ACL => [ 3, 2 ], B => [ 0, 2 ] },
#
#   means that when C1C2C3 is equal to 011 (3) and so we can :
#      - NEVER read keyA
#      - write keyA using KeyB
#      - read ACL with any key (either KeyA or KeyB)
#      - write ACL using KeyB
#      - NEVER read KeyB
#      - write KeyB using KeyB
trailer_acl = {
    #  | KEYA   R  W  | ACL      R  W  | KEYB   R  W   | 
    0: { 'a': [ 0, 1 ], 'acl': [ 1, 0 ], 'b': [ 1, 1 ] },
    1: { 'a': [ 0, 1 ], 'acl': [ 1, 1 ], 'b': [ 1, 1 ] },
    2: { 'a': [ 0, 1 ], 'acl': [ 1, 0 ], 'b': [ 1, 0 ] },
    4: { 'a': [ 0, 2 ], 'acl': [ 3, 0 ], 'b': [ 0, 2 ] },
    3: { 'a': [ 0, 2 ], 'acl': [ 3, 2 ], 'b': [ 0, 2 ] },
    5: { 'a': [ 0, 0 ], 'acl': [ 3, 2 ], 'b': [ 0, 0 ] },
    6: { 'a': [ 0, 0 ], 'acl': [ 3, 0 ], 'b': [ 0, 0 ] },
    7: { 'a': [ 0, 0 ], 'acl': [ 3, 0 ], 'b': [ 0, 0 ] }
}



# Internal representation of TABLE 4 (M001053_MF1ICS50_rev5_3.pdf)
# the key are the actual ACL bits (C1 C2 C3) ,
# the value holds read, write, increment and decrement/restore conditions for the datablock
# possible values for any operation are :
#    0 - operation not possible
#    1 - operation possible using Key A
#    2 - operation possible using Key B
#    3 - operation possible using either Key A or Key B
#
# for instance: 
#
#   4 => [ 3, 2, 0, 0 ],
#   
#   means that when C1C2C3 is equal to 100 (4) and so we can :
#       - read the block using any key (either KeyA or KeyB)
#       - write the block using KeyB
#       - never increment the block
#       - never decrement/restore the block
#
data_acl = {              # read, write, increment, decrement/restore/transfer
    0: [ 3, 3, 3, 3 ],    #  A|B   A|B      A|B        A|B
    1: [ 3, 0, 0, 3 ],    #  A|B   never    never      A|B
    2: [ 3, 0, 0, 0 ],    #  A|B   never    never      never
    3: [ 2, 2, 0, 0 ],    #  B     B        never      never
    4: [ 3, 2, 0, 0 ],    #  A|B   B        never      never
    5: [ 2, 0, 0, 0 ],    #  B     never    never      never
    6: [ 3, 2, 2, 3 ],    #  A|B   B        B          A|B
    7: [ 0, 0, 0, 0 ]     #  never never    never      never
}



class Tag(rfid.libnfc.modulation.iso14443a.br106.tag.Tag):
    def __init__(self, reader, target):
        super(Tag,self).__init__(reader, target)
        self._keys = Classic_Keys.keys
        self._trailer_cache = {}


    def read_block(self, block, noauth=False):
        '''Works only for data blocks, whereas for the trailer blocks reads the ACL only'''
        if not noauth: self.auth(block, READ)
        data = mifare.read(self.reader, block)
        sector = self.block2sector(block)
        tblock = self.trailer_block(sector)
        if block == tblock:
            data = self.fix_trailer_block(sector, data)
        return data



    def write_block(self, block, data, force=False):
        '''Works for data blocks only'''
        sector = self.block2sector(block)
        tblock = self.trailer_block(sector)
        # don't write on trailer blocks unless explicitly requested (force is True)
        if block == tblock and not force:
            raise RuntimeError('Use the force Luke!')

        self.auth(block, WRITE)
        return mifare.write(self.reader, block, data)



    def write_sector(self, sector, data):
        '''Write only the data blocks, ignore the trailer block.'''
        nblocks = self.sector_size(sector)
        start = self.trailer_block(sector) + 1 - nblocks
        offset = 0
        self.auth(start, WRITE)
        for block in (start, start + nblocks - 1):
            self.write_block(block, data[offset:offset+16])
            offset += 16



    def read_sector(self, sector):
        '''For trailer blocks only the non-key part is assumed to be readable.'''
        nblocks = self.sector_size(sector)
        start = self.trailer_block(sector) + 1 - nblocks
        data = ''
        self.auth(start, READ)
        for block in range(start, start + nblocks):
            newdata = self.read_block(block, noauth=True)
            data += newdata

        return data



    def fix_trailer_block(self, sector, data):
        keya, access_cond, keyb = struct.unpack('6s4s6s', data)
        
        keya = struct.pack('>Q', self._keys[sector]['a'])
        keya, = struct.unpack('2x6s', keya)

        keyb = struct.pack('>Q', self._keys[sector]['b'])
        keyb, = struct.unpack('2x6s', keyb)
        
        return struct.pack('6s4s6s', keya, access_cond, keyb)



    def auth(self, block, access_type):
        '''Authentication needs to be done once per sector. After successful authentication any 
        number of blocks from the sector can be read/written to.'''
        # find out the sector we are going to access
        sector = self.block2sector(block)
        # only do the authentication if we have required keys loaded
        if sector >= len(self._keys):
            raise RuntimeError('Cannot unlock sector %d - no key for the sector provided!' % (sector))

        # check the access conditions for this data block
        tblock = self.trailer_block(sector)
        auth_key = 0
        if sector in self._trailer_cache:
            tdata = self._trailer_cache[sector]
        else:
            # we have read the trailer block, se have to authenticate to the sector anyway
            if mifare.auth(self.reader, block, mifare.MC_AUTH_A, self._keys[sector]['a'], self.uid()):
                auth_key = 1
            elif mifare.auth(self.reader, block, mifare.MC_AUTH_B, self._keys[sector]['b'], self.uid()):
                auth_key = 2
            else:
                raise RuntimeError('Cannot unlock sector %d' % (sector))
            tdata = self._trailer_cache[sector] = mifare.read(self.reader, tblock)
        
        keya, access_cond, keyb = struct.unpack('6s4s6s', tdata)
        access_cond = self._parse_acl(access_cond)
        
        sblock = block % self.sector_size(sector)
        # read or write access condition, see data_acl for data blocks and trailer_acl for the trailer block
        auth_keys = access_cond[sblock][access_type] if block != tblock else access_cond[sblock]['acl'][access_type]
        if auth_keys == 0:
            raise RuntimeError("ACL denies %s on sector %d, block %d" % (['reads','writes'][access_type], sector, i))

        if not auth_keys & auth_key:
            keytype = mifare.MC_AUTH_B if auth_keys == 2 else mifare.MC_AUTH_A
            keyidx = 'a' if keytype == mifare.MC_AUTH_A else 'b'
            if not mifare.auth(self.reader, block, keytype, self._keys[sector][keyidx], self.uid()):
                raise RuntimeError('Authentication of sector %d, block %d failed' % (sector, i))

        return True



    # ACL decoding according to specs in M001053_MF1ICS50_rev5_3.pdf
    def _parse_acl(self, data):
        b1, b2, b3, b4 = struct.unpack('4B', data)
        # TODO - extend to doublecheck using inverted flags (as suggested in the spec)
        c1, c2, c3 = (b2 >> 4, b3 & 0x0f, b3 >> 4)
        access_mode = [        
            ((c1 >> block_no) & 1) << 2
            | ((c2 >> block_no) & 1) << 1
            | ((c3 >> block_no) & 1)
            for block_no in range(0, 4)
        ]
        access_mode = [
            data_acl[access_mode[block]] if block != 3 else trailer_acl[access_mode[block]] 
            for block in range(0, 4)
        ]
        return access_mode



    # compute the trailer block number for a given sector
    def trailer_block(self, sector):
        if sector < 32:
            return ((sector+1) * 4) -1
        else:
            return 127 + ((sector - 31) * 16)


    
    # block size in bytes
    def block_size(self):
        return 16

        

    # sector size in blocks
    def sector_size(self, sector):
        return 4 if sector < 32 else 16



    # number of blocks in the tag
    def blocks(self):
        raise RuntimeError('You need to extend this class defining the layout of the tag')

        

    # number of sectors in the tag
    def sectors(self):
        raise RuntimeError('You need to extend this class defining the layout of the tag')


        
    def block2sector(self, block):
        if block < 128:         # small data blocks : 4 x 16 bytes
            return block // 4
        else:                     # big datablocks : 16 x 16 bytes
            return 32 + (block - 128)//16;


    
    def is_trailer_block(self, block):
        return True if (block < 128 and block % 4 == 3) or block % 16 == 15 else False



    def set_key(self, sector, keyA, keyB):
        self._keys[sector] = {'a':keyA, 'b':keyB}

        
    
    def set_keys(self, keys):
        self._keys = keys

        

    def load_keys(self, keyfile):
        with open(keyfile, 'rb') as f:
            self._keys = eval(f.read(), {'__builtins__':[]}, {})
        return self._keys

