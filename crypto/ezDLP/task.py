from Crypto.Util.number import getPrime, isPrime, bytes_to_long
from math import gcd
import os
import random

l = 512
p = getPrime(l)
g = getPrime(l)

flag = 'flag{' + os.urandom(16).hex() + '}'
with open('flag.txt', 'w') as f:
    f.write(flag)
x = bytes_to_long(flag.encode() + os.urandom(l // 8 - 1 - len(flag)))
a = pow(g, x, p ** getPrime(9))
with open('output.txt', 'w') as f:
    f.write('p = ' + str(p) + '\n')
    f.write('g = ' + str(g) + '\n')
    f.write('a = ' + str(a) + '\n')