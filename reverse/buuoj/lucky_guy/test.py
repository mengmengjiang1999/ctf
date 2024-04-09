# GXY{do_not_~dn^fsbg

# flag{do_not_~dn^fsbg}

# 
# 

from pwn import *
context.terminal=['tmux','splitx','-h']
context.log_level='debug'

# p=remote("121.37.132.113",10001)


# p=process("./luck_guy")

# # payload=136*b'A'+4*b'B'+p32(0x8048320)+4*b'0'+p32(0x0804A024)
# payload=b'2'
# p.sendafter(b'please input a lucky number\n',payload)

# # p.sendline(payload)
# p.interactive()

# f=b'7f666f6067756369'

f='7f666f6067756369'

s= "GXY{do_not_"


# flag{%d%d2069a45792d233ac}
f=[0x7f,0x66,0x6f,0x60,0x67,0x75,0x63,0x69][::-1]

for j in range(0,8):
    if j %2==1:
        v1=f[j]-2
    else:
        v1=f[j]-1
    s+=chr(v1)

f2=[]

for item in f:
    f2.append(chr(item))
    
# print(''.join(f2))

print(s)


# 0x7e646e5e66736267
# 0x7e646e5e66736267

#   s = 9180147350284624745LL;

# 0x7f666f6067756369

# for ( j = 0; j <= 7; ++j )
#         {
#           if ( j % 2 == 1 )
#             v1 = *(&f2 + j) - 2;
#           else
#             v1 = *(&f2 + j) - 1;
#           *(&f2 + j) = v1;
#         }
