from base64 import b64encode as b32encode
from base64 import b64decode
from gmpy2 import invert,gcd,iroot
from Crypto.Util.number import *
from binascii import a2b_hex,b2a_hex
import random

flag = "******************************"

nbit = 128


p = 177077389675257695042507998165006460849
n = 37421829509887796274897162249367329400988647145613325367337968063341372726061
q=211330365658290458913359957704294614589

phi = (p-1)*(q-1)

# e = random.randint(50000,70000)
es=[]
for i in range(49999,70000):
	if gcd(i,phi) == 1:
		es.append(i)


print(es)
print(len(es))

# c = pow(int(b2a_hex(flag),16),e,n)

c=  int(b64decode(str("==gMzYDNzIjMxUTNyIzNzIjMyYTM4MDM0gTMwEjNzgTM2UTN4cjNwIjN2QzM5ADMwIDNyMTO4UzM2cTM5kDN2MTOyUTO5YDM0czM3MjM"[::-1])))


for e in es:
	d=pow(e,-1,phi)
	m=pow(c,d,n)
	flag=long_to_bytes(m)
	if 'flag' in str(flag):
		print(flag)

# print(long_to_bytes(m))

# print(b32encode(str(c))[::-1])

# 2373740699529364991763589324200093466206785561836101840381622237225512234632
