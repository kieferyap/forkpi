'''RFID Tag base abstract class'''
# Author: Boris Mazic
# Date: 29.05.2012
#package rfid.libnfc.tag


class Tag(object):
    def __init__(self, reader, target):
        self.reader = reader
        self.target = target

