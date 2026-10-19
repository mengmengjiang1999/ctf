m=2**3

print(m)
print(m//2)

from Crypto.Util.number import *
from random import randint
from gmpy2 import *

ra = 8607
amin=(ra//2)**4
print(amin)
print(int(amin).bit_length())
# 342835182924481

rb = 7150
bmin=(rb//2)**4
print(bmin)
print(int(bmin).bit_length())
# 163344375390625


print(int(amin**8).bit_length())

s=1<<129
for i in range(s,s+10):
    pass