from Crypto.Util.number import *
from secret import flag

def GenKey(nbit):
    p, q = getPrime(nbit // 2), getPrime(nbit // 2)
    n = p * q
    e = getPrime(56)
    d = inverse(e, (p - 1) * (q - 1))
    return (n, e), (p, q, d)

def GenGift(nbit, pk, sk):
    n, e = pk
    p, q, d = sk
    k = (e * d - 1) // ((p - 1) * (q - 1))
    x = getPrime(nbit // 2)
    c = x * (p + q) % d
    return k, x >> (nbit // 4), c

nbit = 1024
pk, sk = GenKey(nbit)
gift = GenGift(nbit, pk, sk) 

n, e = pk
enc = pow(bytes_to_long(flag), e, n)

f = open("data.txt","w")
f.write(f"pk = {pk}\n")
f.write(f"gift = {gift}\n")
f.write(f"enc = {enc}\n")
f.close()
