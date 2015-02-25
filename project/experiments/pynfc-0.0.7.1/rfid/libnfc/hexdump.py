'''Hex Dump Utility'''
# Author: Boris Mazic
# Date: 04.06.2012
#package rfid.libnfc.hexdump



def hexbytes(xs, group_size=1, byte_separator=' ', group_separator=' '):
    def ordc(c):
        return ord(c) if isinstance(c,str) else c
    
    if len(xs) <= group_size:
        s = byte_separator.join('%02X' % (ordc(x)) for x in xs)
    else:
        r = len(xs) % group_size
        s = group_separator.join(
            [byte_separator.join('%02X' % (ordc(x)) for x in group) for group in zip(*[iter(xs)]*group_size)]
        )
        if r > 0:
            s += group_separator + byte_separator.join(['%02X' % (ordc(x)) for x in xs[-r:]])
    return s



def hexprint(xs):
    def chrc(c):
        return c if isinstance(c,str) else chr(c)
    
    def ordc(c):
        return ord(c) if isinstance(c,str) else c
    
    def isprint(c):
        return ordc(c) > 31 if isinstance(c,str) else c > 31
    
    return ''.join([chrc(x) if isprint(x) else '.' for x in xs])



def hexdump(xs, group_size=4, byte_separator=' ', group_separator='-', printable_separator='  ', address=0, address_format='%04X', line_size=16):
    if address is None:
        s = hexbytes(xs, group_size, byte_separator, group_separator)
        if printable_separator:
            s += printable_separator + hexprint(xs)
    else:
        r = len(xs) % line_size
        s = ''
        bytes_len = 0
        for offset in range(0, len(xs)-r, line_size):
            chunk = xs[offset:offset+line_size]
            bytes = hexbytes(chunk, group_size, byte_separator, group_separator)
            s += (address_format + ': %s%s\n') % (address + offset, bytes, printable_separator + hexprint(chunk) if printable_separator else '')
            bytes_len = len(bytes)
        
        if r > 0:
            offset = len(xs)-r
            chunk = xs[offset:offset+r]
            bytes = hexbytes(chunk, group_size, byte_separator, group_separator)
            bytes = bytes + ' '*(bytes_len - len(bytes))
            s += (address_format + ': %s%s\n') % (address + offset, bytes, printable_separator + hexprint(chunk) if printable_separator else '')
    
    return s



if __name__ == '__main__':
    print hexdump('a\nb\rc\f\vdef\t')
    print hexdump('a\nb\rc\f\vdef\t', printable_separator='  ')
    print hexdump('a\nb\rc\f\vdef\t', byte_separator=' ')
    print hexdump('a\nb\rc\f\vdef\t', byte_separator=' ', printable_separator='  ')
    print hexdump('Why don\'t you love the bluebells, love?', byte_separator=' ', group_size=8, group_separator='-', printable_separator='  ', address=12)
    print hexdump('Why don\'t you love the bluebells, love?', byte_separator=' ', group_size=4, group_separator='-', printable_separator='  ', address=12)
    print hexdump('Why don\'t you love the bluebells, love?', byte_separator=' ', group_size=4, group_separator='-', printable_separator='  ', address=13, line_size=7)
