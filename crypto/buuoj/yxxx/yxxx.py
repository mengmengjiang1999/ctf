


f=open("./c.txt","r")
g=open("./key.txt","r")

c=f.readline()
k=g.readline()

print(c)
print(k)

m=""
for i in range(len(c)):
    m+=chr(ord(c[i])^ord(k[i]))
print(m)