ns=[]
cs=[]
with open("./rsa5.txt","r")as f:
    lines=f.readlines()
    for l in range(len(lines)//3):
        ns.append(int(lines[l*3][4:]))
        cs.append(int(lines[l*3+1][4:]))
print(ns)
print(cs)

import gmpy2

for item1 in ns:
    for item2 in ns:
        p = gmpy2.gcd(item1, item2)
        if p!=1 and item1!=item2:
            print("n1="+str(item1))
            print("n2="+str(item2))
            print(p)
            print("\n\n")
    
