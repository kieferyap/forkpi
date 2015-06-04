# From http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[:-ord(s[len(s)-1:])]

import base64
import hashlib
from Crypto import Cipher
from Crypto import Random

class AES:
    def __init__( self, key ):
        self.key = hashlib.md5(key.encode()).hexdigest()

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( Cipher.AES.block_size )
        cipher = Cipher.AES.new( self.key, Cipher.AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw.encode() ) ) 

    def decrypt( self, enc ):
        enc = base64.b64decode(enc.encode())
        iv = enc[:16]
        cipher = Cipher.AES.new(self.key, Cipher.AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] )).decode()