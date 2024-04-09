from Crypto.Util.number import long_to_bytes,bytes_to_long

e=65537
n=86934482296048119190666062003494800588905656017203025617216654058378322103517
p=285960468890451637935629440372639283459
q=304008741604601924494328155975272418463

phi=(p-1)*(q-1)
d = pow(e, -1, phi)

with open("./flag.enc","rb+")as f:
    c=f.read()
    cl=bytes_to_long(c)
    m=pow(cl,d,n)
    print(long_to_bytes(m))
    
    