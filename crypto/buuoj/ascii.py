# l=['11111','4157','16614','5123','14514','3165','16215','1164','17112','6145','16217','1115','16514','3150']
# l=['111','114','157','166','145','123','145','143','165','162','151','164','171','126','145','162','171','115','165','143','150']
# c=[]
# ccc=''
# for item in l:
#     print(int(item,8))
#     # print(chr(int(item,8)))
#     ccc+=chr(int(item,8))
#     c.append(int(item,8))
#     print(ccc)



ccc="83 89 78 84 45 86 96 45 115 121 110 116 136 132 132 132 108 128 117 118 134 110 123 111 110 127 108 112 124 122 108 118 128 108 131 114 127 134 108 116 124 124 113 108 76 76 76 76 138 23 90 81 66 71 64 69 114 65 112 64 66 63 69 61 70 114 62 66 61 62 69 67 70 63 61 110 110 112 64 68 62 70 61 112 111 112"


c=ccc.split(" ")
print(c)
m=''

for i in range(len(c)):
    c[i]=int(c[i])
print(c)

for item in c:
    # print(chr(int(item)))
    print(item)
    print(chr(item))
    m+=chr(item)
print(m)

print(ord('`'))
print(ord('S'))

mmm=''
for item in c:
    ttt=chr(item)
    # if item>=ord('A')and item<=ord('Z'):
    #     ttt=chr(ord('A')+(item-13-ord('A')+26)%26)
    # elif item>=ord('a')and item<=ord('z'):
    #     ttt=chr(ord('a')+(item-13-ord('a')+26)%26)
    # else:
    ttt=chr(item-13)
    print(ttt)
    mmm+=ttt
print(mmm)

print(len('wwwyshiyanbarycomyisyveryygoodyYYYY'))
print(len('MDOT3ReNc3O2R0Se1O01RPS20aac3Q1S0cbc'))



'''
FLAG IS flag{www_shiyanbar_com_is_very_good_????}
MD5:38e4c352809e150186920aac37190cbc
'''

import hashlib
import re


md5de="38e4c352809e150186920aac37190cbc"

for a in range(33,127):
    for b in range(33,127):
        for c in range(33,127):
            for d in range(33,127):
                flag="flag{www_shiyanbar_com_is_very_good_"+chr(a)+chr(b)+chr(c)+chr(d)+"}"
                print(flag)
                m=hashlib.md5()
                m.update(flag.encode())
                des=m.hexdigest()
                print(des)
                if md5de in des:
                    print(des)
                    break
                