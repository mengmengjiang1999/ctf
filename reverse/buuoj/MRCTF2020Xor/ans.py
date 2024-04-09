c='MSAWB~FXZ:J:`tQJ"N@ bpdd}8g'

flag=''

for i in range(len(c)):
    flag+=chr(i^ord(c[i]))
    
print(flag)

# print(chr(0x4D))