from Crypto.Util.number import getPrime, bytes_to_long
from math import gcd
import os

l = 512
e = 65537
while True:
    p = getPrime(l)
    q = getPrime(l)
    N = p * q
    phi = (p - 1) * (q - 1)
    if p != q and gcd(phi, e) == 1:
        break
d = pow(e, -1, phi)
flag = 'flag{' + os.urandom(16).hex() + '}'
with open('flag.txt', 'w') as f:
    f.write(flag)
m = bytes_to_long(flag.encode() + os.urandom(l * 2 // 8 - 1 - len(flag)))
c = pow(m, e, N)
dp = d % (p - 1)
with open('output.txt', 'w') as f:
    f.write('N = ' + str(N) + '\n')
    f.write('e = ' + str(e) + '\n')
    f.write('c = ' + str(c) + '\n')
    f.write('dp = ' + str(dp) + '\n')