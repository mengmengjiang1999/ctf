f=open("./output.txt","r")

lines=f.readlines()

flag=""
print(lines)
print(len(lines))

for i in range(1,20,1):
    line=int(lines[i-1])
    if i&1>0:
        print(1)
        flag+=chr(line>>i)
    else:
        print(0)
        flag+=chr(int(line/i))
    print(flag)
        
print(flag)