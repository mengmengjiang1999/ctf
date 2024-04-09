import os
import binascii
import struct


misc = open("image.png","rb").read()

data = misc[12:16] + struct.pack('>i',690)+ misc[20:29]
crc32 = binascii.crc32(data) & 0xffffffff

print(crc32)
print(hex(crc32))

# # for i in range(1024):
# data = misc[12:29] #+ struct.pack('>i',i)+ misc[20:29]
# crc32 = binascii.crc32(data) & 0xffffffff
# print(crc32)
# print(hex(crc32))