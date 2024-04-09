from pwn import *

context.terminal=['tmux','splitx','-h']
context.log_level='debug'

p=remote("192.168.4.250",10024)

# p=process("./test")

p.sendline(b'2')

p.interactive()


# RHZP8-V2QKE-Z1ZPQ-QFUET-Q7QZZ