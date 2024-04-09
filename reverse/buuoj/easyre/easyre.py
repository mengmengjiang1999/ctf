# 1. PEiD查壳
# 2. UPX Easy GUI 脱壳

# scanf("%s", &v19);
#   if ( (_BYTE)v19 != 65 || HIBYTE(v19) != 67 || v20 != 84 || v21 != 70 || v22 != 123 || v26 != 125 )
#     return 0;
#   v16 = v23;
#   v17 = v24;
#   v18 = v25;


data='~}|{zyxwvutsrqponmlkjihgfedcba`_^]\[ZYXWVUTSRQPONMLKJIHGFEDCBA@?>=<;:9876543210/.-,+*)(\'&%$# !"'
byte='~}|{zyxwvutsrqponmlkjihgfedcba`_^]\[ZYXWVUTSRQPONMLKJIHGFEDCBA@?>=<;:9876543210/.-,+*)(\'&%$# !"'


print(hex(65))
print(hex(67))
print(hex(84))
print(hex(70))
print(hex(123))
print(hex(125))

print(chr(65))
print(chr(67))
print(chr(84))
print(chr(70))
print(chr(123))
print(chr(125))


v=['0']*16

v[4 ]=chr( 42)
v[5 ]=chr( 70)
v[6 ]=chr( 39)
v[7 ]=chr( 34)
v[8 ]=chr( 78)
v[9 ]=chr( 44)
v[10] =chr( 34)
v[11] =chr( 40)
v[12] =chr( 73)
v[13] =chr( 63)
v[14] =chr( 43)
v[15] =chr( 64)

print(chr(0x27))

# for i in range(11):

print(''.join(v))

flag=''

for i in range(12):
    flag+=chr(data.find(v[4+i])+1)
    # print(chr(data.find(v[4+i])+1))
    
print(flag)
    
# ACTF{+G(#O-#)J@,A}
