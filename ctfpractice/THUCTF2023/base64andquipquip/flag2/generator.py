import os
import random
import base64

def step1():
    # generate a table
    table1=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    random.shuffle(table1)
    # table2=list("abcdefghijklmnopqrstuvwxyz")
    table2=""
    for item in table1:
        table2+=item.lower()
    # random.shuffle(table2)
    
    # base64Table=list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    # random.shuffle(base64Table)

    base64Table="".join(table1)+"".join(table2)+"0123456789+/"
    with open("./table.txt","w")as f:
        f.write(base64Table+"\n")
        # flag="THUCTF{W31c0me_T0_Bas3}"
        flag="THUCTF{I_10u3_6as3b4}"
        f.write(flag)

def step2():
    # run base64 encode
    os.system("g++ main.cpp base64.h base64.cpp -o main")
    os.system("./main < ./table.txt > ./encoded.txt")
    
def step3():
    with open("./table.txt","r")as f:
        base64Table=f.readline().strip()
        flag=f.readline().strip()
    with open("./encoded.txt","r")as g:
        encoded=g.readline()
    string1 = base64Table#修改之后的base64表

    string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"  #原来的表
    
    print(string1)
    print(string2)

    flagdecoded=base64.b64decode(encoded.translate(str.maketrans(string1,string2)))
    print(str(flagdecoded).strip())
    print(flag)
    if flagdecoded==flag:
        print("true")
    else:
        print("false")

if __name__=='__main__':
    # step1()
    # step2()
    step3()