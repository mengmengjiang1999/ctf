import os
# import secret
from Crypto.Cipher import AES
from hashlib import sha256

LEGAL=b"0123456789abcdef"

class Sign:
    def __init__(self):
        self.key = os.urandom(16)
        self.iv = os.urandom(16)
        self.flag = secret.flag
        assert(self.flag.startswith(b'flag{') and self.flag.endswith(b'}'))
        assert(all(_ in LEGAL for _ in self.flag[5:-1]))
    
    def pad(self, msg):
        need = 16 - (len(msg) & 0xf)
        return msg + need * bytes([need])
        
    def unpad(self, msg):
        return msg[:-msg[-1]]
        
    def encrypt(self, msg, iv):
        cipher = AES.new(key = self.key, mode = AES.MODE_CBC, iv = iv)
        ct = cipher.encrypt(self.pad(msg))
        return ct
    
    def decrypt(self, ct, iv):
        cipher = AES.new(key = self.key, mode = AES.MODE_CBC, iv = iv)
        msg = cipher.decrypt(ct)
        return self.unpad(msg)
    
    def verify(self, ct, iv):
        msg = self.decrypt(ct, iv)
        for a, b in zip(self.flag, msg):
            if(a != b):
                return "Invaild!"
        return "Valid!"

if __name__ == "__main__":
    
    baby = Sign()
    
    menu="""
[G]et: get encrypted flag
[H]ash: get hash
[V]erify: verify your encrypted flag 
"""
    print(menu)
    
    while(True):
        type = input(">")
        
        if(type == "G"):
            ct = baby.encrypt(baby.flag, baby.iv)
            print(ct.hex())
        
        elif(type == "H"):
            hash = sha256(baby.flag).hexdigest()
            print(hash)
        
        elif(type == "V"):
            msg = bytes.fromhex(input("input your message >").replace(" ","").strip())
            iv = bytes.fromhex(input("input your iv >").replace(" ","").strip())
            res = baby.verify(msg,iv)
            print(res)
        
        else:
            print("Try again!")
