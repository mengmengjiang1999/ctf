code = ['\x1f', '\x12', '\x1d', '(', '0', '4', '\x01', '\x06', '\x14', '4', ',', 
 '\x1b', 'U', '?', 'o', '6', '*', ':', '\x01', 'D', ';', '%', '\x13']

# print(len(code))

# len(code)==23
# flag的长度从1到22都有可能

# for l in range(0,22):
flag=''
l=len(code)
for i in range(l-2,-1,-1):
    print("i="+str(i))
    print(code[i])
    print(code[i+1])
    print(ord(code[i]))
    print(ord(code[i+1]))
    code[i] = chr(ord(code[i]) ^ ord(code[i + 1]))
for i in range(l):
    num=chr(((ord(code[i]) - i + 128) % 128 + 128) % 128)
    flag += num
        
print(flag)