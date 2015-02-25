"""Python functions to handle the ISO-14443-A protocol basics (parity and CRC)"""

#  Pynfc is a python wrapper for the libnfc library
#  Copyright (C) 2009  Mike Auty
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

def crc(inbytes):
    """Calculates the ISO-14443A CRC checksum"""
    wCrc = 0x6363

    for i in range(len(inbytes)):
        byte = ord(inbytes[i])
        byte = (byte ^ (wCrc & 0x00FF))
        byte = ((byte ^ (byte << 4)) & 0xFF)
        wCrc = ((wCrc >> 8) ^ (byte << 8) ^ (byte << 3) ^ (byte >> 4)) & 0xFFFF

    res = chr(wCrc & 0xFF) + chr((wCrc >> 8) & 0xff)
    return res

def parity(inbytes):
    """Calculates the odd parity bits for a byte string"""
    res = ""
    for i in inbytes:
        tempres = 1
        for j in range(8):
            tempres = tempres ^ ((ord(i) >> j) & 0x1)
        res += chr(tempres)
    return res
