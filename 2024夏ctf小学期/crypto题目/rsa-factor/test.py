from Crypto.Util.number import getPrime, bytes_to_long,long_to_bytes
from math import gcd
import os

l = 128
e = 65537
while True:
    p = 180520419233472586343713862406512351947
    q = 210844540544468919392274030927212100563
    N = p * q
    phi = (p - 1) * (q - 1)
    if p != q and gcd(phi, e) == 1:
        break
d = pow(e, -1, phi)
flag = "flag\{8b986411ef5f9798\}"
# m = bytes_to_long(flag.encode() + os.urandom(l * 2 // 8 - 1 - len(flag)))
c = 8252166413974795558605878185033153263532264800491935392593141049838362497564
m=pow(c,d,N)
c2=pow(m,e,N)
# print(c)
# print(c2)
mb=long_to_bytes(m)[:-(l * 2 // 8 - 1 - len(flag))]
print(mb)
print(mb.decode())
with open('output2.txt', 'w') as f:
    f.write('N = ' + str(N) + '\n')
    f.write('e = ' + str(e) + '\n')
    f.write('m = ' + str(m) + '\n')
    # f.write('flag = '+str(m))