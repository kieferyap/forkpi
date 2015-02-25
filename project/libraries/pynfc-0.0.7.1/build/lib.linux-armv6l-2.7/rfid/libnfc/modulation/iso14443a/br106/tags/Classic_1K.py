'''MIFARE Classic 1K tag concrete class'''
# Author: Boris Mazic
# Date: 30.05.2012
#package rfid.libnfc.modulation.iso14443a.br106.tags.Classic_1K

from rfid.libnfc.modulation.iso14443a.br106.tags import Classic


class Tag(Classic.Tag):
    def __init__(self, reader, target):
        super(Tag,self).__init__(reader, target)



    # number of blocks in the tag
    def blocks(self):
        return 16*4

        
        
    # number of sectors in the tag
    def sectors(self):
        return 16

        

