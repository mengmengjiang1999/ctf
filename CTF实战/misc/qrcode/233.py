# -*- coding: utf-8 -*-

import binascii
import base64
import string
import itertools
import struct

# alph = '0123456789'
alph = '0123456789'

crcdict = {}
print("computing all possible CRCs...")
for x in itertools.product(list(alph), repeat=4):
    st = ''.join(x)
    testcrc = binascii.crc32(bytes(st,"ascii"))
    # print(hex(testcrc))
    print(hex(testcrc)[2:])
    crcdict[hex(testcrc)[2:]] = st
print("Done!")

# f = open('00000000.zip',"rb")
# data = f.read()
# f.close()
# print(data[14:18])
# crc = ''.join(data[14:18])
# crc = "ae4c3446"
crc="46344cae"
if crc in crcdict:
    print(crcdict[crc])
else:
    print("FAILED!")
    
# print(crcdict)