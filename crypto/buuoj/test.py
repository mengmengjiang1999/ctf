from Crypto.Util.number import *
import base64



s1="synt{5pq1004q-86n5-46q8-o720-oro5on0417r1}"
s2=""

for item in s1:
    if ord(item)>=ord("a") and ord(item)<=ord("z"):
        s2+=chr(ord("z")-(ord(item)-ord("a"))-1)
    elif ord(item)>=ord("0") and ord(item)<=ord("9"):
        s2+=chr(ord("9")-(ord(item)-ord("0")))
    else:
        s2+=item
       
       
print(s2) 

s3=s2.split("-")


s2=s2[::-1]
print(s2)

s4=""
for item in s3:
    s4+=item[::-1]+"-"
    
"flag{i5998ij4-4l31-1i35-972k-8h2859lk4khk-}"
    
print(s4)