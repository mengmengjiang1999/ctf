c="6 1 6 6 6 3 7 4 6 6 7 B 3 1 7 3 2 7 7 4 5 F 7 3 3 0 5 F 3 3 3 4 3 5 7 9 7 D "
c.strip()
print(c.replace(" ",''))

c="61666374667B317327745F73305F333435797D"

sss=""
for i in range(0,len(c),2):
    s=c[i:i+2]
    print(s)
    ss=int(s,base=16)
    print(chr(ss))
    sss+=chr(ss)
print(sss)