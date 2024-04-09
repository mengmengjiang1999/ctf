from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p=remote("111.231.174.57",10001)
# p=process("./controller_pwn")


payload1=hex("baa".encode('latin-1'))
payload2=hex("caa".encode('latin-2'))

# print()

# p.interactive()