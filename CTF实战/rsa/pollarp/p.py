from Crypto.Util.number import GCD

def algorithm(n,B):
    a=2
    for j in range(2,B):
        a=pow(a,j,n)
        print(a)
    d=GCD(a-1,n)
    print("d="+str(d))
    if d>1 and d<n:
        return d
    else:
        return -1
    
n=15770708441
B=180

print("=====")
print(algorithm(n,B))