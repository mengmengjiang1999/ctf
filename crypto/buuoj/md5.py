import hashlib   
import re

def md555():
    for i in range(32,127):
        for j in range(32,127):
            for k in range(32,127):
                m=hashlib.md5()
                m.update(('TASC'+chr(i)+'O3RJMV'+chr(j)+'WDJKX'+chr(k)+'ZM').encode())
                des=m.hexdigest()
                if 'e9032' in des and 'da' in des and '911513' in des:
                    print(des)
            
            
def md666():
    for i in range(32,127):
        for j in range(32,127):
            for k in range(32,127):
                m=hashlib.md5()
                m.update(('TASC'+chr(i)+'O3RJMV'+chr(j)+'WDJKX'+chr(k)+'ZM').encode())
                des=m.hexdigest()
                h=r'e903...4dab....08.....51.80..8a.'
                pattern=re.compile(h)
                result=pattern.findall(des)
                if result!=[]:
                    print(des.upper())
                    print('TASC'+chr(i)+'O3RJMV'+chr(j)+'WDJKX'+chr(k)+'ZM')
                
md666()
                
# s="101999966233"
# m=hashlib.md5()
# m.update(s.encode())
# print(m.hexdigest())

# m="TASC O3RJMV WDJKX ZM"
# ml=m.split()
# for item1 in range("A","Z"):
#     for item2 in range("A","Z"):
#         for item3 in range("A","Z"):
#                 s=ml[0]+item1+ml[1]+item2+ml[2]+item3+ml[3]

# h="E903...4DAB....08.....51.80..8A."
