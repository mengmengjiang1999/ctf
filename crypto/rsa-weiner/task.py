from Crypto.Util.number import getPrime, isPrime, bytes_to_long
from math import gcd
import os
import random

l = 512
while True:
    p = getPrime(l)
    q = p + 2 ** 420
    while not isPrime(q):
        q += 2
    N = p * q
    phi = (p - 1) * (q - 1)
    while True:
        d = random.randint(2, N ** 0.32)
        if gcd(d, phi) == 1:
            e = pow(d, -1, phi)
            break
    break

flag = 'flag{' + os.urandom(16).hex() + '}'
with open('flag.txt', 'w') as f:
    f.write(flag)
m = bytes_to_long(flag.encode() + os.urandom(l * 2 // 8 - 1 - len(flag)))
c = pow(m, e, N)
with open('output.txt', 'w') as f:
    f.write('N = ' + str(N) + '\n')
    f.write('e = ' + str(e) + '\n')
    f.write('c = ' + str(c) + '\n')