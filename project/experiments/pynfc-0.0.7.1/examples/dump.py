#!/usr/bin/python
# coding=utf-8
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

# Author: Boris Mazic
# Date: 06.06.2012
# Abstract:
#    Dump the contents of a MIFARE Classic card.



# python -i dump.py keys-B7006691.py B7006691.bin

import argparse
from rfid.libnfc import pynfc, reader
from rfid.libnfc.hexdump import hexdump


def dump_card(keyfile, outfile, verbosity):
    r = reader.Reader(verbosity=verbosity)
    if not r.init(): raise RuntimeError('Cannot initialise the RFID reader!')
    print r

    tag = r.connect(modtype=pynfc.NfcDevice.NMT_ISO14443A, baudrate=pynfc.NfcDevice.NBR_106)
    print tag

    tag.load_keys(keyfile)

    data = ''
    for i in range(0,tag.sectors()):
        data += tag.read_sector(i)

    if verbosity > 0:
        print hexdump(data, byte_separator=' ', group_size=4, group_separator='-', printable_separator='  ', address=0)
    
    with open(outfile, 'wb') as f:
        f.write(data)



def main():
    parser = argparse.ArgumentParser(description='Dump the contents of an ISO14443A_106 compliant card (eg. MIFARE Classic)')
    parser.add_argument('keyfile', help='a file name containing the card keys in the format [{"a":keya,"b":keyb}+]')
    parser.add_argument('outfile', help='the output file where the card contents will be dumped')
    parser.add_argument('-v', '--verbosity', type=int, default=1, help='verbosity level, 0 turns it off')
    args = parser.parse_args()
    dump_card(args.keyfile, args.outfile, args.verbosity)


main()