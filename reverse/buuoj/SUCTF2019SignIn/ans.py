v7=0xad939ff59f6e70bcbfad406f2494993757eee98b91bc244184a377520d06fc35

byte_202010=[0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x61,0x62, 0x63, 0x64, 0x65, 0x66]

# print(len(v7))
# print(len(byte_202010))

# v[8]是7*16个字节

# 经过处理后v9=v7
# a1=&v8,a2=&v9

# size_t __fastcall sub_96A(const char *a1, __int64 a2)
# {
#   size_t result; // rax
#   int v3; // [rsp+18h] [rbp-18h]
#   int i; // [rsp+1Ch] [rbp-14h]

#   v3 = 0;
#   for ( i = 0; ; i += 2 )
#   {
#     result = strlen(a1);
#     if ( v3 >= result )
#       break;
#     *(_BYTE *)(a2 + i) = byte_202010[(char)(a1[v3] >> 4)];  # v9[0]=byte_202010[v8[0]>>4]
#     *(_BYTE *)(a2 + i + 1LL) = byte_202010[a1[v3++] & 0xF]; # v9[1]=byte_202010[v8[0]&0x1111]
#   }
#   return result;
# }

from Crypto.Util.number import long_to_bytes
n=103461035900816914121390101299049044413950405173712170434161686539878160984549
e=65537
p=282164587459512124844245113950593348271
q=366669102002966856876605669837014229419
phi=(p-1)*(q-1)
d=pow(e,-1,phi)
c=int(v7)
m=pow(c,d,n)

print(m)

# m=185534734614696481020381637136165435809958101675798337848243069

v=long_to_bytes(m)
print(v)
print(len(v))

flag=""

b="".join(chr(item)for item in byte_202010)
print(b)

for i in range(0,len(v),2):
    print(v[i],v[i+1])
    index1=byte_202010.index(ord(v[i]))
    index2=byte_202010.index(ord(v[i+1]))
    print(index1,index2,int(index1),int(index2),bin((index1<<4)+index2))
    flag+=chr((index1<<4)+index2)
    print(flag)