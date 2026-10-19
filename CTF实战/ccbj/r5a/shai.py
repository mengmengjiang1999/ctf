

primes=[True]*(1<<30)

primes[2]=True

for i in range(2,len(primes)):
    if primes[i]==True:
        for j in range(i+i,len(primes),i):
            primes[j]=False
            
p=[]
for i in range(2,len(primes)):
    if primes[i]:
        p.append(i)

print(p)