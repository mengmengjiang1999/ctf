'''
达芬奇隐藏在蒙娜丽莎中的数字列:
1 233 3 2584 1346269 144 5 196418 21 1597 610 377 10946 89 514229 987 8 55 6765 2178309 121393 317811 46368 4181 1 832040 2 28657 75025 34 13 17711 
记录在达芬奇窗台口的神秘数字串:
36968853882116725547342176952286
'''



key='1 233 3 2584 1346269 144 5 196418 21 1597 610 377 10946 89 514229 987 8 55 6765 2178309 121393 317811 46368 4181 1 832040 2 28657 75025 34 13 17711'
cipher='36968853882116725547342176952286'
message='36968853882116725547342176952286'

keys=key.split()
print(keys)
print(len(keys))
for i in range(len(keys)):
    keys[i]=int(keys[i])
print(keys)

fibonacci=[]
s=1
t=1
fibonacci.append(s)
fibonacci.append(t)
for i in range(35):
    a=s+t
    fibonacci.append(a)
    s=t
    t=a
print(fibonacci)

pos=[]
for item in keys:
    for i in range(len(fibonacci)):
        if item==fibonacci[i]:
            pos.append(i)
            break
            
print(pos)
pos[0]=1
print(pos)

m=['a']*32
for i in range(len(pos)):
    m[pos[i]]=cipher[i]
for item in m:
    print(item,end='')
