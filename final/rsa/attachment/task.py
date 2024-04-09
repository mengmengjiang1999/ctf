from Crypto.Util.number import *
from secret import m, p, q

nbit = 2048

assert(isPrime(p) and p >= 2**(nbit-1))
assert(isPrime(q) and q >= 2**(nbit-1))
assert(p != q)

n = p * q
e = 3
phi = (p-1) * (q-1)

assert(GCD(e, phi) == 1)

d = inverse(e, phi)
m = bytes_to_long(m)
c1 = pow(m, e, n)
c2 = pow(m+1, e, n)

with open('rsa.txt', 'w') as f:
    print(n, file=f)
    print(c1, file=f)
    print(c2, file=f)
