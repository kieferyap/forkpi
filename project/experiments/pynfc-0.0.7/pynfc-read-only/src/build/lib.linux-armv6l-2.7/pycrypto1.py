"""Pycrypto1 module, based on public domain optimized code by I.C.Weiner"""

#  Pynfc is a python wrapper for the libnfc library
#  Copyright (C) 2009  Mike Auty
#  PyCrypto1 is based on public domain optimized code by I.C.Weiner
#  See (http://cryptolib.com/ciphers/crypto1/crypto1.c)
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

def bytes_to_long(in_bytes):
    """Converts a byte string into a long"""
    hexstr = ''.join(["%0.2x" % ord(byte) for byte in in_bytes])
    return int(hexstr, 16)

def long_to_bytes(in_long, length = 4):
    """Converts a long into a byte string of length of length
       If the long is larger than the length, the most-significant bytes will be dropped 
    """
    out_bytes = ""
    while length > 0:
        out_bytes = chr(in_long & 0xFF) + out_bytes
        in_long = in_long >> 8
        length -= 1
    return out_bytes

class Crypto1():
    """Maintains the state of the crypto1 algorithm"""

    mf1_f4a = 0x9E98
    mf1_f4b = 0xB48E
    mf1_f5c = 0xEC57E80A

    def __init__(self, ckey = None):
        self.state = 0xFFFFFFFFFFFF
        if ckey is not None:
            self.set_key(ckey)

    def set_key(self, ckey):
        """Resets the internal state of the crypto1 algorithm by setting it to a key"""
        if isinstance(ckey, str):
            ckey = bytes_to_long(ckey)
        print "key: %0.12X" % ckey
        self.state = 0
        # Flip the bytes, as we do with all other byte ordered values
        for x in range(64):
            self.state += self.bit(ckey, x ^ 56) << x ^ 56
        # Since we're only working with 48 bits out of 64, shift back 16
        self.state = self.state >> 16

    def bit(self, x, n):
        """Returns the nth bit of x"""
        return (x >> n) & 1

    def rev8(self, x):
        """Reverses 8-bits"""
        return ((((x) >> 7) & 1) ^ ((((x) >> 6) & 1) << 1) ^ ((((x) >> 5) & 1) << 2) ^ ((((x) >> 4) & 1) << 3) ^ ((((x) >> 3) & 1) << 4) ^ ((((x) >> 2) & 1) << 5) ^ ((((x) >> 1) & 1) << 6) ^ (((x) & 1) << 7))

    def rev16(self, x):
        """Reverses 16-bits"""
        return (self.rev8(x) ^ (self.rev8(x >> 8) << 8))

    def rev32(self, x):
        """Reverses 32 bits"""
        return (self.rev16(x) ^ (self.rev16(x >> 16) << 16))

    def prng_next(self, x, n):
        """PRNG next number"""
        x = self.rev32(x)
        for _ in range(n):
            x = (x << 1) + (((x >> 15) ^ (x >> 13) ^ (x >> 12) ^ (x >> 10)) & 1)
        return self.rev32(x)

    def i4(self, x, a, b, c, d): #pylint: disable-msg=R0913
        """Builds up a 4-bit number from the ath, bth, cth and dth bits of x"""
        return ((((x) >> (a)) & 1) + (((x) >> (b)) & 1) * 2 + (((x) >> (c)) & 1) * 4 + (((x) >> (d)) & 1) * 8)

    def nf20(self, x):
        """Returns the nonlinear-feedback for state x"""
        i5 = ((self.mf1_f4b >> self.i4(x, 9, 11, 13, 15)) & 1) * 1 + \
             ((self.mf1_f4a >> self.i4(x, 17, 19, 21, 23)) & 1) * 2 + \
             ((self.mf1_f4a >> self.i4(x, 25, 27, 29, 31)) & 1) * 4 + \
             ((self.mf1_f4b >> self.i4(x, 33, 35, 37, 39)) & 1) * 8 + \
             ((self.mf1_f4a >> self.i4(x, 41, 43, 45, 47)) & 1) * 16

        return (self.mf1_f5c >> i5) & 1

    def lf18(self, x):
        """Returns the linear-feeback for state x"""
        return  (((x >> 0) ^ (x >> 5) ^ (x >> 9) ^ (x >> 10) ^ (x >> 12) ^ (x >> 14) \
                ^ (x >> 15) ^ (x >> 17) ^ (x >> 19) ^ (x >> 24) ^ (x >> 25) ^ (x >> 27) \
                ^ (x >> 29) ^ (x >> 35) ^ (x >> 39) ^ (x >> 41) ^ (x >> 42) ^ (x >> 43)) & 1)

    def get_bit(self, in_bit, fb):
        """Completes a round of crypto1"""
        x = self.state

        lf = self.lf18(x)
        nf = self.nf20(x)
        x = (x >> 1) ^ ((in_bit ^ (lf if fb & 1 else 0) ^ (nf if fb & 2 else 0)) << 47)
        self.state = x
        return nf

    def get_word (self, in_word, fb):
        """Applies crypto1 to a 32-bit word
           fb specifies whether the linear (|1) and non-linear feedback (|2) is included
        """
        o = 0
        for ci in range(32):
            o += self.get_bit(self.bit(in_word, ci ^ 24), fb) << (ci ^ 24)
        return o

    def xor_bytes(self, a, b):
        """Returns the xor of two byte strings"""
        return long_to_bytes(bytes_to_long(a) ^ bytes_to_long(b), max(len(a), len(b)))

    def encrypt_parity_word(self, par, ks_first, ks_next):
        """Encrypts an 8-byte parity string (\x01\x00\x01...),
           which should be the correct (cleartext parity of the Reader Challenge and Reader Response)"""
        p = []
        for x in range(3):
            p.append(chr(ord(par[x]) ^ self.bit(ks_first, (8 * (x + 1)) ^ 24)))
        p.append(chr(ord(par[3]) ^ self.bit(ks_next, 24)))
        return ''.join(p)

class Crypto1Stream(object):
    """Creates a crypto1 stream capable of providing stream material on a per bit level"""

    def __init__(self, crypto1, initstream = None, inlen = None):
        if initstream is None:
            initstream = ""
        self.c1 = crypto1
        self.stream = initstream
        self.streamlen = len(initstream) * 8
        if inlen is not None:
            self.steamlen = inlen

    def _extend_stream(self):
        """Extends the stream by adding on another word"""
        next_word = self.c1.get_word(0, 1)
        modulo = self.streamlen % 8
        if modulo > 0:
            self.stream += long_to_bytes(next_word << modulo + ord(self.stream[-1])) + chr(next_word >> ((8 * 4) - modulo))
        else:
            self.stream += long_to_bytes(next_word)
        self.streamlen += 4 * 8

    def get_stream(self, bitlen, use = True):
        """Returns bitlen bits of keystream"""
        while self.streamlen < bitlen:
            self._extend_stream()
        modulo = bitlen % 8
        output = self.stream[:bitlen / 8]
        if modulo > 0:
            output += chr(ord(self.stream[bitlen / 8]) & (0xFF >> (8 - modulo)))
        if use:
            self.stream = self.stream[bitlen / 8:]
            if modulo > 0:
                for x in range(len(self.stream) - 1):
                    self.stream = self.stream[:x] + chr((ord(self.stream[x]) >> modulo) + ((ord(self.stream[x + 1]) << modulo) & 0xFF)) + self.stream[x + 1:]
                self.stream = self.stream[:len(self.stream) - 1] + chr(ord(self.stream[len(self.stream) - 1]) >> modulo)
            self.streamlen -= bitlen
        return output

    def get_xored_parity(self, parbytes):
        """Returns the required parity bits for a string of bytelen length"""
        xpar = self.get_stream((len(parbytes) + 1) * 8, False)
        xparbytes = ""
        for x in range(len(parbytes)):
            xparbytes += chr(ord(parbytes[x]) ^ (ord(xpar[x + 1]) & 0x1))
        return xparbytes

    def get_xored_output(self, inbytes, bitlen, par):
        """Return encrypted output"""
        if len(inbytes) < (bitlen + 7) / 8:
            raise RuntimeError("Crypto1: get_xored_output called with fewer bytes than bitlen")
        xpar = None
        if bitlen > 8:
            xpar = self.get_xored_parity(par)
        xbytes = self.get_stream(bitlen)
        outbytes = ""
        for x in range((bitlen + 7) / 8):
            outbytes += chr(ord(xbytes[x]) ^ ord(inbytes[x]))
        return outbytes, bitlen, xpar


if __name__ == '__main__':
    key = [0xFFFFFFFFFFFF, 0xFFFFFFFFFFFF, 0xFFFFFFFFFFFF, 0xFFFFFFFFFFFF, 0xFFFFFFFFFFFF, 0xFFFFFFFFFFFF, 0xFFFFFFFFFFFF, 0xFFFFFFFFFFFF]
    ID = [0x7BED1AFD, 0x7BED1AFD, 0x7BED1AFD, 0x7BED1AFD, 0x7BED1AFD, 0x7BED1AFD, 0x7BED1AFD, 0x7BED1AFD]
    TC = [0x01020304, 0x02030405, 0x03040506, 0x04050607, 0x05060708, 0x06070809, 0x0708090A, 0x08090A0B]   # Tag Challenge
    RC = [0x12345678, 0x23456789, 0x3456789A, 0x456789AB, 0x56789ABC, 0x6789ABCD, 0x789ABCDE, 0x89ABCDEF]   # Reader Challenge
    RR = [0x8D3A9A9C, 0x525BF719, 0xB3B6BCF5, 0x8D58D582, 0x1A4389AD, 0x8E791939, 0x6D3566AF, 0x870B0215]   # Reader response (next(64, TC))
    TR = [0x7208E6C6, 0xBBEF66AE, 0xC622FC7F, 0x21741A05, 0xE350ACD9, 0xD0240BF8, 0xF0B5A5C5, 0x8AD097B3]
    KS = [
        [0xF0293188, 0x96188BA7, 0x8743C386, 0x4BAFEEF2, 0x9F5B3C53],
        [0x6C5976CF, 0x4B2F94B8, 0x77B92595, 0xDDB19335, 0xB811C5A5],
        [0x7E55F18D, 0xE0AB17F7, 0xFFCF6559, 0x131E7093, 0x7145E26B],
        [0xBFDC7361, 0x9403B607, 0x26E4D8F2, 0xFEBAB9F0, 0x81AEB1C9],
        [0xD556A1EC, 0x8759D54D, 0xC5B10ACE, 0xB6A9C3CD, 0x94F5A51C],
        [0x0916465B, 0x0A9AE66B, 0x31EF4F79, 0x044D4505, 0xEE4125C4],
        [0x99C49847, 0x525B1DE4, 0xB7F78842, 0xF3A36608, 0x72E92768],
        [0xFEA22F39, 0x3B809753, 0x9893345F, 0x82371E6D, 0xBB9DEFAF],
    ]

    for k in range(len(key)):
        s = Crypto1()
        s.set_key(key[k])
        # Input the crypto1 UID xored with the Tag Challenge
        s.get_word(ID[k] ^ TC[k], 1)
        # Input the crypto1 Reader Challenge, and decrypt it
        s.get_word(RC[k]        , 3)

        print "UID: %0.8X" % ID[k]
        print "Tag Challenge: %0.8X" % TC[k]
        print "(Encrypted) Reader Challenge: %0.8X" % RC[k]
        print "(Encrypted) Reader Response: %0.8X" % RR[k]
        print "(Encrypted) Tag Response: %0.8X" % TR[k]
        print "(Encrypted) Tag Command: %0.8X" % KS[k][0]
        print "(Encrypted) Tag Data: %0.8X %0.8X %0.8X %0.8X" % (KS[k][1], KS[k][2], KS[k][3], KS[k][4])
        print "%s" % ((s.prng_next(TC[k], 64) ^ s.get_word(0, 1)) == RR[k]),
        print "%s" % ((s.prng_next(TC[k], 96) ^ s.get_word(0, 1)) == TR[k]),
        for i in range(5):
            print "%08lX" % (KS[k][i] ^ s.get_word(0, 1)),
        print "\n"


