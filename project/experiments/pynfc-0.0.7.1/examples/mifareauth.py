"""Test for a simple Mifare NFC Authentication"""

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

import sys
from rfid.libnfc import pynfc, pycrypto1, py14443a



def hex_dump(string):
    """Dumps data as hexstrings"""
    return ' '.join(["%0.2X" % ord(x) for x in string])

### NFC device setup
devs = pynfc.list_devices()
if not devs:
    print "No readers found"
    sys.exit(1)
dev = devs[0]
# Connect to the reader
print "Connect to reader:",
nfc = dev.connect(target = False)
print bool(nfc)
# Set tup the various connection fields
print "Easy Framing False:", nfc.configure(nfc.NDO_EASY_FRAMING, False)
print "Field Down:", nfc.configure(nfc.NDO_ACTIVATE_FIELD, False)
print "CRC False:", nfc.configure(nfc.NDO_HANDLE_CRC, False)
print "Parity True:", nfc.configure(nfc.NDO_HANDLE_PARITY, True)
print "Field Up:", nfc.configure(nfc.NDO_ACTIVATE_FIELD, True)

# Start the run with the tag
init = nfc.transceive_bits("\x26", 7)
if (not init):
    raise RuntimeError("Failed to initialize reader")

# Create a Crypto1 object, set the key  
crypto1 = pycrypto1.Crypto1()
crypto1.set_key(0xA0A1A2A3A4A5)

# Since we're using transceive_bytes,  
nfc.configure(nfc.NDO_HANDLE_PARITY, True)
msg = "\x93\x20"
print "R -> T:", hex_dump(msg)
uid = nfc.transceive_bytes(msg)
print "T -> R:", hex_dump(uid)
U_l = pycrypto1.bytes_to_long(uid[:4])

msg = "\x93\x70" + uid + py14443a.crc("\x93\x70" + uid)
print "R -> T:", hex_dump(msg)
select = nfc.transceive_bytes(msg)
if (not select):
    raise RuntimeError("Failed to select card")
print "T -> R:", hex_dump(select)

# We turn the parity handling OFF when sending our own
# Our auth message is for key type A on block 4
msg = "\x60\x00" + py14443a.crc("\x60\x00")
nfc.configure(nfc.NDO_HANDLE_PARITY, False)
print "R -> T:", hex_dump(msg)
authresp = nfc.transceive_bits(msg, 32, py14443a.parity(msg))

if not authresp:
    raise RuntimeError("Failed during authentication request")

TN, bits, parity = authresp
print "T -> R:", hex_dump(TN)
TN_l = pycrypto1.bytes_to_long(TN)
RR_l = crypto1.prng_next(TN_l, 64)

# Input the UID xor TN for the first state
# Since we're not doing nested auth, we don't care about the output    
crypto1.get_word(U_l ^ TN_l, 1)

# Set an arbitrary RC (next of TN), this can probably be anything
# Then generate the next states for crypto1
RC_l = crypto1.prng_next(TN_l, 32)
RC_x = crypto1.get_word(RC_l, 1)
RR_x = crypto1.get_word(0, 1)

# Calculate this now, because we'll need the first bit for sending our response
TR_x = crypto1.get_word(0, 1)

# Make the cleartext response, calculate the cleartext parity, then encrypt the parity             
msg = pycrypto1.long_to_bytes(RC_l) + pycrypto1.long_to_bytes(RR_l)
par = py14443a.parity(msg)
# Encrypt the message, then the parity
msg = pycrypto1.long_to_bytes(RC_l ^ RC_x) + pycrypto1.long_to_bytes(RR_l ^ RR_x)
xpar = crypto1.encrypt_parity_word(par[:4], RC_x, RR_x) + crypto1.encrypt_parity_word(par[4:], RR_x, TR_x)

print "R -> T:", hex_dump(msg)
authresp2 = nfc.transceive_bits(msg, 64, xpar)
if not authresp2:
    raise RuntimeError("Failed to authenticate, check the key is correct")

TR, bits, TR_par = authresp2
print "T -> R:", hex_dump(TR)
print "TR == Next(TN, 96):", (pycrypto1.bytes_to_long(TR) ^ TR_x) == crypto1.prng_next(TN_l, 96)

ks1 = crypto1.get_word(0, 1)
ks2 = crypto1.get_word(0, 1)

msg = "\x30\x00" + py14443a.crc("\x30\x00")
par = py14443a.parity(msg)

msg = pycrypto1.long_to_bytes(pycrypto1.bytes_to_long(msg) ^ ks1)
xpar = crypto1.encrypt_parity_word(par, ks1, ks2)

print "R -> T:", hex_dump(msg)

res = nfc.transceive_bits(msg, 4 * 8, xpar)

if not res:
    raise RuntimeError("Failed to transceive for some reason")

(data, bits, par) = res
print "T -> R:", hex_dump(pycrypto1.long_to_bytes(pycrypto1.bytes_to_long(data[:4]) ^ ks2))
