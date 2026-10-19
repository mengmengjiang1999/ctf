
import os
import random
import pickle
from hashlib import sha256
from signal import  alarm
from string import ascii_letters, digits
FLAG = os.environ.get("FLAG", "flag{XXX_FAKE_FLAG_XXX}")

class Server:
    def __init__(self):
        alarm(60)
        if self.generate_key() and self.proof_of_work(): 
            self.service()

    def Login(self, vk):
        username = input("username: ")
        if username == "Nu1L@root":
            token = bytes.fromhex(input("Gimme ur token: "))
            if self.verify(username, token, vk):
                return 1
            print("Some Error...")
        else:
            print("user does not exists...") 

    def generate_key(self):
        sk = [os.urandom(32) for _ in range(32)]
        vk = [self.hash(x, 256) for x in sk]
        with open("/app/key.pub", 'wb') as f:
            pickle.dump(vk, f)
        with open("/app/key.priv", 'wb') as f:
            pickle.dump(sk, f)
        return True

    def load_key(self):
        with open("/app/key.pub", 'rb') as f:
            vk = pickle.load(f)
        with open("/app/key.priv", 'rb') as f:
            sk = pickle.load(f)
        return vk, sk

    def hash(self, x, n):
        for _ in range(n):
            x = sha256(x).digest()
        return x

    def sign(self, msg, sk):
        h = self.hash(msg, 1)
        sig = b''.join([self.hash(x, 256 - n) for x, n in zip(sk, h)])
        return sig

    def verify(self, msg, sig, vk):
        block = [sig[i:i+32] for i in range(0, len(sig), 32)]
        h = self.hash(msg.encode(), 1)
        vk_ = [self.hash(x, n) for x, n in zip(block, h)]
        return vk_ == vk

    def service(self):
        vk, sk = self.load_key()
        msg = bytes.fromhex(input('ur msg (hex): '))
        if msg == "Nu1L@root": return 0
        sig = self.sign(msg, sk)
        print('ur signature (hex):', sig.hex())
        if self.Login(vk):
            print(f"Oh admin, flag here: {FLAG}")

    def proof_of_work(self):
        proof = ''.join([random.choice(ascii_letters + digits) for _ in range(20)])
        digest = sha256(proof.encode('latin-1')).hexdigest()
        print('sha256(XXXX + {}) == {}'.format(proof[4: ], digest))
        print('Give me XXXX:')
        x = input()
        if x != proof[: 4]:
            return False
        return True

Server()