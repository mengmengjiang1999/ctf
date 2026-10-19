from pwn import *
from Crypto.Cipher import AES

# context.log_level = "debug"

io = process(["python3", "babySign.py"])
io.recvuntil(b">")

flag_begin = "flag{"

io.sendline(b"G")
flag_enc = io.recvline().strip()
flag_enc = bytes.fromhex(flag_enc.decode())

last_block = flag_enc[-16:]

blocks = [flag_enc[i:i+16] for i in range(0, len(flag_enc), 16)]
# print(len(blocks))


def try_decrypt(msg, iv):
    io.recvuntil(b">")
    io.sendline(b"V")
    io.recvuntil(b">")
    io.sendline(msg.hex().encode())
    io.recvuntil(b">")
    io.sendline(iv.hex().encode())
    ret = io.recvline().strip()
    if b"Valid" in ret:
        return True
    if b"Invaild" in ret:
        return False
    raise Exception("Invalid response: " + ret.hex())

def gen_padding_iv(pad_len):
    c = bytearray(last_block[:])
    c[-1] = pad_len ^ last_byte
    return bytes(c)

def guess_last_byte():
    charset = list(range(1,17))
    for i in charset:
        c = bytearray(last_block[:])
        c[-1] = i ^ 255 ^ flag_enc[-17]
        second_block = bytes(c)
        enc = second_block*15+last_block
        for j in range(256):
            iv = bytes([j]*16)
            if try_decrypt(enc, iv):
                print("Found last byte:", i)
                return i ^ flag_enc[-17]
        

last_byte = guess_last_byte() 


