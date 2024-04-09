# function(c){return String.fromCharCode((c <= "Z" ? 90 : 122) >= (c = c.charCodeAt(0) + 13) ? c : c - 26);}
# (c <= "Z" ? 90 : 122)如果c是大写字母那么变成90，如果c是小写字母那么变成122
# (c = c.charCodeAt(0) + 13)c的charCode+13
# 如果c的charCode+13<=90或charCode+13<=122仍然是a-zA-Z中的一个那么输出结果是它-26
# 否则的话就输出c
# if

c="PyvragFvqrYbtvafNerRnfl@syner-ba.pbz"
flag=''

for item in c:
    if ord(item)+26<=77 or ord(item)+26>=90 and ord(item)+26<=109:
        flag+=chr(ord(item)+26)
    else:
        # flag+=chr(ord(item)-26)
        flag+=item
    print(flag)
    
# jyvrag`vqrYbtvafherlnflZsynerGbaHpbz

# 
# flag{}

string=""
for item in range(34,127):
    string+=chr(item)

def func(c):
    c1=ord(c)
    if ord(c)<=ord("Z"):
        c1=90
    else:
        c1=122
    c2=ord(c)+13
    if c1>=c2:
        return c
    else:
        return chr(ord(c)-26)
    
m="flag{23333}"

print(string)

string2="".join(func(item)for item in string)
print(string2)

# ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz
# ABCDEFGHIJKLM456789:;<=>?@[\]^_`abcdefghijklmTUVWXYZ[\]^_`

