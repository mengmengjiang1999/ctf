from struct import pack, unpack
import os
from math import sin

def leftrotate(x,r):
    x&=0xffffffff
    return ((x<<r)|(x>>(32-r)))&0xffffffff

def thisiscipher(pt, key):
    r = [7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22, 5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20 , 4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21 ]
    k = []
    for i in range(64):
        k.append(int(abs(sin(i + 1)) * 2**32))
       
    assert len(key)==64
    assert len(pt)%16==0

    ct = b""

    for ii in range(0, len(pt), 16):
        a = unpack('I',pt[ii:ii+4])[0]
        b = unpack('I',pt[ii+4:ii+8])[0]
        c = unpack('I',pt[ii+8:ii+12])[0]
        d = unpack('I',pt[ii+12:ii+16])[0]
        w = []
        for j in range(16):
            w.append(unpack('I', key[j*4:j*4+4])[0])
        for i in range(64):
            if i<16:
                f = (b & c) | ((~b) & d)
            elif i<32:
                f = (b & d) | ((~d) & c)
            elif i<48:
                f = b ^ c ^ d
            else:
                f = c ^ (b | (~d))

            if i<16:
                g = i
            elif i<32:
                g = (5*i+1)%16
            elif i<48:
                g = (3*i+5)%16
            else:
                g = (7*i)%16

            tmp = d
            d = c
            c = b
            b = (leftrotate(a+f+k[i]+w[g], r[i])+b) & 0xffffffff
            a = tmp

        ct += pack('I',a)+pack('I',b)+pack('I',c)+pack('I',d)
    return ct

def thisishash(msg):
    key = b'\xc0Oy\x86IL\xab\xac\rj\x16\xe9=o\x87\xc4\x04\xb0\xadh2\xf1\xf4=.\xd5c_L\xf2\xce\x87\xbcc\xbb\t\xc4\x12\x1b\xf9t\xec4\x914\xdf\xa6\x13\xb7\x96Z\r\xe1\x1at\x9b\x9dO7\xa4\xcb\x1e\xc3\x14'
    return thisiscipher(msg,key)

if __name__ == "__main__":
    flag = open("flag",'rb').read()
    while len(flag)%16 != 0:
        flag += b'\x00'
    key = b'\xc0Oy\x86IL\xab\xac\rj\x16\xe9=o\x87\xc4\x04\xb0\xadh2\xf1\xf4=.\xd5c_L\xf2\xce\x87\xbcc\xbb\t\xc4\x12\x1b\xf9t\xec4\x914\xdf\xa6\x13\xb7\x96Z\r\xe1\x1at\x9b\x9dO7\xa4\xcb\x1e\xc3\x14'
    ct = thisiscipher(flag, key)
    print(ct)
    with open("ciphertext",'wb') as f:
        f.write(ct)
